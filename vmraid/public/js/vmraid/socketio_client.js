vmraid.socketio = {
	open_tasks: {},
	open_docs: [],
	emit_queue: [],
	init: function(port = 3000) {
		if (!window.io) {
			return;
		}

		if (vmraid.boot.disable_async) {
			return;
		}

		if (vmraid.socketio.socket) {
			return;
		}

		//Enable secure option when using HTTPS
		if (window.location.protocol == "https:") {
			vmraid.socketio.socket = io.connect(vmraid.socketio.get_host(port), {secure: true});
		}
		else if (window.location.protocol == "http:") {
			vmraid.socketio.socket = io.connect(vmraid.socketio.get_host(port));
		}
		else if (window.location.protocol == "file:") {
			vmraid.socketio.socket = io.connect(window.localStorage.server);
		}

		if (!vmraid.socketio.socket) {
			console.log("Unable to connect to " + vmraid.socketio.get_host(port));
			return;
		}

		vmraid.socketio.socket.on('msgprint', function(message) {
			vmraid.msgprint(message);
		});

		vmraid.socketio.socket.on('eval_js', function(message) {
			eval(message);
		});

		vmraid.socketio.socket.on('progress', function(data) {
			if(data.progress) {
				data.percent = flt(data.progress[0]) / data.progress[1] * 100;
			}
			if(data.percent) {
				if(data.percent==100) {
					vmraid.hide_progress();
				} else {
					vmraid.show_progress(data.title || __("Progress"), data.percent, 100, data.description);
				}
			}
		});

		vmraid.socketio.setup_listeners();
		vmraid.socketio.setup_reconnect();

		$(document).on('form-load form-rename', function(e, frm) {
			if (frm.is_new()) {
				return;
			}

			for (var i=0, l=vmraid.socketio.open_docs.length; i<l; i++) {
				var d = vmraid.socketio.open_docs[i];
				if (frm.doctype==d.doctype && frm.docname==d.name) {
					// already subscribed
					return false;
				}
			}

			vmraid.socketio.doc_subscribe(frm.doctype, frm.docname);
		});

		$(document).on("form-refresh", function(e, frm) {
			if (frm.is_new()) {
				return;
			}

			vmraid.socketio.doc_open(frm.doctype, frm.docname);
		});

		$(document).on('form-unload', function(e, frm) {
			if (frm.is_new()) {
				return;
			}

			// vmraid.socketio.doc_unsubscribe(frm.doctype, frm.docname);
			vmraid.socketio.doc_close(frm.doctype, frm.docname);
		});

		$(document).on('form-typing', function(e, frm) {
			vmraid.socketio.form_typing(frm.doctype, frm.docname);
		});

		$(document).on('form-stopped-typing', function(e, frm) {
			vmraid.socketio.form_stopped_typing(frm.doctype, frm.docname);
		});

		window.addEventListener('beforeunload', () => {
			if (!cur_frm || cur_frm.is_new()) {
				return;
			}

			// if tab/window is closed, notify other users
			if (cur_frm.doc) {
				vmraid.socketio.doc_close(cur_frm.doctype, cur_frm.docname);
			}
		});
	},
	get_host: function(port = 3000) {
		var host = window.location.origin;
		if(window.dev_server) {
			var parts = host.split(":");
			port = vmraid.boot.socketio_port || port.toString() || '3000';
			if(parts.length > 2) {
				host = parts[0] + ":" + parts[1];
			}
			host = host + ":" + port;
		}
		return host;
	},
	subscribe: function(task_id, opts) {
		// TODO DEPRECATE

		vmraid.socketio.socket.emit('task_subscribe', task_id);
		vmraid.socketio.socket.emit('progress_subscribe', task_id);

		vmraid.socketio.open_tasks[task_id] = opts;
	},
	task_subscribe: function(task_id) {
		vmraid.socketio.socket.emit('task_subscribe', task_id);
	},
	task_unsubscribe: function(task_id) {
		vmraid.socketio.socket.emit('task_unsubscribe', task_id);
	},
	doc_subscribe: function(doctype, docname) {
		if (vmraid.flags.doc_subscribe) {
			console.log('throttled');
			return;
		}

		vmraid.flags.doc_subscribe = true;

		// throttle to 1 per sec
		setTimeout(function() { vmraid.flags.doc_subscribe = false }, 1000);

		vmraid.socketio.socket.emit('doc_subscribe', doctype, docname);
		vmraid.socketio.open_docs.push({doctype: doctype, docname: docname});
	},
	doc_unsubscribe: function(doctype, docname) {
		vmraid.socketio.socket.emit('doc_unsubscribe', doctype, docname);
		vmraid.socketio.open_docs = $.filter(vmraid.socketio.open_docs, function(d) {
			if(d.doctype===doctype && d.name===docname) {
				return null;
			} else {
				return d;
			}
		})
	},
	doc_open: function(doctype, docname) {
		// notify that the user has opened this doc, if not already notified
		if (!vmraid.socketio.last_doc
			|| (vmraid.socketio.last_doc[0] != doctype || vmraid.socketio.last_doc[1] != docname)) {
			vmraid.socketio.socket.emit('doc_open', doctype, docname);

			vmraid.socketio.last_doc &&
				vmraid.socketio.doc_close(vmraid.socketio.last_doc[0], vmraid.socketio.last_doc[1]);
		}
		vmraid.socketio.last_doc = [doctype, docname];
	},
	doc_close: function(doctype, docname) {
		// notify that the user has closed this doc
		vmraid.socketio.socket.emit('doc_close', doctype, docname);

		// if the doc is closed the user has also stopped typing
		vmraid.socketio.socket.emit('doc_typing_stopped', doctype, docname);
	},
	form_typing: function(doctype, docname) {
		// notifiy that the user is typing on the doc
		vmraid.socketio.socket.emit('doc_typing', doctype, docname);
	},
	form_stopped_typing: function(doctype, docname) {
		// notifiy that the user has stopped typing
		vmraid.socketio.socket.emit('doc_typing_stopped', doctype, docname);
	},
	setup_listeners: function() {
		vmraid.socketio.socket.on('task_status_change', function(data) {
			vmraid.socketio.process_response(data, data.status.toLowerCase());
		});
		vmraid.socketio.socket.on('task_progress', function(data) {
			vmraid.socketio.process_response(data, "progress");
		});
	},
	setup_reconnect: function() {
		// subscribe again to open_tasks
		vmraid.socketio.socket.on("connect", function() {
			// wait for 5 seconds before subscribing again
			// because it takes more time to start python server than nodejs server
			// and we use validation requests to python server for subscribing
			setTimeout(function() {
				$.each(vmraid.socketio.open_tasks, function(task_id, opts) {
					vmraid.socketio.subscribe(task_id, opts);
				});

				// re-connect open docs
				$.each(vmraid.socketio.open_docs, function(d) {
					if(locals[d.doctype] && locals[d.doctype][d.name]) {
						vmraid.socketio.doc_subscribe(d.doctype, d.name);
					}
				});

				if (cur_frm && cur_frm.doc) {
					vmraid.socketio.doc_open(cur_frm.doc.doctype, cur_frm.doc.name);
				}
			}, 5000);
		});
	},
	process_response: function(data, method) {
		if(!data) {
			return;
		}

		// success
		var opts = vmraid.socketio.open_tasks[data.task_id];
		if(opts[method]) {
			opts[method](data);
		}

		// "callback" is std vmraid term
		if(method==="success") {
			if(opts.callback) opts.callback(data);
		}

		// always
		vmraid.request.cleanup(opts, data);
		if(opts.always) {
			opts.always(data);
		}

		// error
		if(data.status_code && data.status_code > 400 && opts.error) {
			opts.error(data);
		}
	}
}

vmraid.provide("vmraid.realtime");
vmraid.realtime.on = function(event, callback) {
	vmraid.socketio.socket && vmraid.socketio.socket.on(event, callback);
};

vmraid.realtime.off = function(event, callback) {
	vmraid.socketio.socket && vmraid.socketio.socket.off(event, callback);
}

vmraid.realtime.publish = function(event, message) {
	if(vmraid.socketio.socket) {
		vmraid.socketio.socket.emit(event, message);
	}
}

