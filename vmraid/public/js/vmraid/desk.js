// Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt
/* eslint-disable no-console */

// __('Modules') __('Domains') __('Places') __('Administration') # for translation, don't remove

vmraid.start_app = function() {
	if (!vmraid.Application)
		return;
	vmraid.assets.check();
	vmraid.provide('vmraid.app');
	vmraid.provide('vmraid.desk');
	vmraid.app = new vmraid.Application();
};

$(document).ready(function() {
	if (!vmraid.utils.supportsES6) {
		vmraid.msgprint({
			indicator: 'red',
			title: __('Browser not supported'),
			message: __('Some of the features might not work in your browser. Please update your browser to the latest version.')
		});
	}
	vmraid.start_app();
});

vmraid.Application = class Application {
	constructor() {
		this.startup();
	}

	startup() {
		vmraid.socketio.init();
		vmraid.model.init();

		if(vmraid.boot.status==='failed') {
			vmraid.msgprint({
				message: vmraid.boot.error,
				title: __('Session Start Failed'),
				indicator: 'red',
			});
			throw 'boot failed';
		}

		this.setup_vmraid_vue();
		this.load_bootinfo();
		this.load_user_permissions();
		this.make_nav_bar();
		this.set_favicon();
		this.setup_analytics();
		this.set_fullwidth_if_enabled();
		this.add_browser_class();
		this.setup_energy_point_listeners();
		this.setup_copy_doc_listener();

		vmraid.ui.keys.setup();

		vmraid.ui.keys.add_shortcut({
			shortcut: 'shift+ctrl+g',
			description: __('Switch Theme'),
			action: () => {
				vmraid.theme_switcher = new vmraid.ui.ThemeSwitcher();
				vmraid.theme_switcher.show();
			}
		});

		this.set_rtl();

		// page container
		this.make_page_container();
		this.set_route();

		// trigger app startup
		$(document).trigger('startup');

		$(document).trigger('app_ready');

		if (vmraid.boot.messages) {
			vmraid.msgprint(vmraid.boot.messages);
		}

		if (vmraid.user_roles.includes('System Manager')) {
			// delayed following requests to make boot faster
			setTimeout(() => {
				this.show_change_log();
				this.show_update_available();
			}, 1000);
		}

		if (!vmraid.boot.developer_mode) {
			let console_security_message = __("Using this console may allow attackers to impersonate you and steal your information. Do not enter or paste code that you do not understand.");
			console.log(
				`%c${console_security_message}`,
				"font-size: large"
			);
		}

		this.show_notes();

		if (vmraid.ui.startup_setup_dialog && !vmraid.boot.setup_complete) {
			vmraid.ui.startup_setup_dialog.pre_show();
			vmraid.ui.startup_setup_dialog.show();
		}

		vmraid.realtime.on("version-update", function() {
			var dialog = vmraid.msgprint({
				message:__("The application has been updated to a new version, please refresh this page"),
				indicator: 'green',
				title: __('Version Updated')
			});
			dialog.set_primary_action(__("Refresh"), function() {
				location.reload(true);
			});
			dialog.get_close_btn().toggle(false);
		});

		// listen to build errors
		this.setup_build_events();

		if (vmraid.sys_defaults.email_user_password) {
			var email_list =  vmraid.sys_defaults.email_user_password.split(',');
			for (var u in email_list) {
				if (email_list[u]===vmraid.user.name) {
					this.set_password(email_list[u]);
				}
			}
		}

		// REDESIGN-TODO: Fix preview popovers
		this.link_preview = new vmraid.ui.LinkPreview();

		if (!vmraid.boot.developer_mode) {
			setInterval(function() {
				vmraid.call({
					method: 'vmraid.core.page.background_jobs.background_jobs.get_scheduler_status',
					callback: function(r) {
						if (r.message[0] == __("Inactive")) {
							vmraid.call('vmraid.utils.scheduler.activate_scheduler');
						}
					}
				});
			}, 300000); // check every 5 minutes

			if (vmraid.user.has_role("System Manager")) {
				setInterval(function() {
					vmraid.call({
						method: 'vmraid.core.doctype.log_settings.log_settings.has_unseen_error_log',
						args: {
							user: vmraid.session.user
						},
						callback: function(r) {
							if (r.message.show_alert) {
								vmraid.show_alert({
									indicator: 'red',
									message: r.message.message
								});
							}
						}
					});
				}, 600000); // check every 10 minutes
			}
		}
	}

	set_route() {
		vmraid.flags.setting_original_route = true;
		if (vmraid.boot && localStorage.getItem("session_last_route")) {
			vmraid.set_route(localStorage.getItem("session_last_route"));
			localStorage.removeItem("session_last_route");
		} else {
			// route to home page
			vmraid.router.route();
		}
		vmraid.after_ajax(() => vmraid.flags.setting_original_route = false);
		vmraid.router.on('change', () => {
			$(".tooltip").hide();
		});
	}

	setup_vmraid_vue() {
		Vue.prototype.__ = window.__;
		Vue.prototype.vmraid = window.vmraid;
	}

	set_password(user) {
		var me=this;
		vmraid.call({
			method: 'vmraid.core.doctype.user.user.get_email_awaiting',
			args: {
				"user": user
			},
			callback: function(email_account) {
				email_account = email_account["message"];
				if (email_account) {
					var i = 0;
					if (i < email_account.length) {
						me.email_password_prompt( email_account, user, i);
					}
				}
			}
		});
	}

	email_password_prompt(email_account,user,i) {
		var me = this;
		let d = new vmraid.ui.Dialog({
			title: __('Password missing in Email Account'),
			fields: [
				{
					'fieldname': 'password',
					'fieldtype': 'Password',
					'label': __('Please enter the password for: <b>{0}</b>', [email_account[i]["email_id"]]),
					'reqd': 1
				},
				{
					"fieldname": "submit",
					"fieldtype": "Button",
					"label": __("Submit")
				}
			]
		});
		d.get_input("submit").on("click", function() {
			//setup spinner
			d.hide();
			var s = new vmraid.ui.Dialog({
				title: __("Checking one moment"),
				fields: [{
					"fieldtype": "HTML",
					"fieldname": "checking"
				}]
			});
			s.fields_dict.checking.$wrapper.html('<i class="fa fa-spinner fa-spin fa-4x"></i>');
			s.show();
			vmraid.call({
				method: 'vmraid.core.doctype.user.user.set_email_password',
				args: {
					"email_account": email_account[i]["email_account"],
					"user": user,
					"password": d.get_value("password")
				},
				callback: function(passed) {
					s.hide();
					d.hide();//hide waiting indication
					if (!passed["message"]) {
						vmraid.show_alert({message: __("Login Failed please try again"), indicator: 'error'}, 5);
						me.email_password_prompt(email_account, user, i);
					} else {
						if (i + 1 < email_account.length) {
							i = i + 1;
							me.email_password_prompt(email_account, user, i);
						}
					}

				}
			});
		});
		d.show();
	}
	load_bootinfo() {
		if(vmraid.boot) {
			this.setup_workspaces();
			vmraid.model.sync(vmraid.boot.docs);
			$.extend(vmraid._messages, vmraid.boot.__messages);
			this.check_metadata_cache_status();
			this.set_globals();
			this.sync_pages();
			vmraid.router.setup();
			moment.locale("en");
			moment.user_utc_offset = moment().utcOffset();
			if(vmraid.boot.timezone_info) {
				moment.tz.add(vmraid.boot.timezone_info);
			}
			if(vmraid.boot.print_css) {
				vmraid.dom.set_style(vmraid.boot.print_css, "print-style");
			}
			vmraid.user.name = vmraid.boot.user.name;
			vmraid.router.setup();
		} else {
			this.set_as_guest();
		}
	}

	setup_workspaces() {
		vmraid.modules = {};
		vmraid.workspaces = {};
		for (let page of vmraid.boot.allowed_workspaces || []) {
			vmraid.modules[page.module]=page;
			vmraid.workspaces[vmraid.router.slug(page.name)] = page;
		}
		if (!vmraid.workspaces['home']) {
			// default workspace is settings for VMRaid
			vmraid.workspaces['home'] = vmraid.workspaces[Object.keys(vmraid.workspaces)[0]];
		}
	}

	load_user_permissions() {
		vmraid.defaults.update_user_permissions();

		vmraid.realtime.on('update_user_permissions', vmraid.utils.debounce(() => {
			vmraid.defaults.update_user_permissions();
		}, 500));
	}

	check_metadata_cache_status() {
		if(vmraid.boot.metadata_version != localStorage.metadata_version) {
			vmraid.assets.clear_local_storage();
			vmraid.assets.init_local_storage();
		}
	}

	set_globals() {
		vmraid.session.user = vmraid.boot.user.name;
		vmraid.session.logged_in_user = vmraid.boot.user.name;
		vmraid.session.user_email = vmraid.boot.user.email;
		vmraid.session.user_fullname = vmraid.user_info().fullname;

		vmraid.user_defaults = vmraid.boot.user.defaults;
		vmraid.user_roles = vmraid.boot.user.roles;
		vmraid.sys_defaults = vmraid.boot.sysdefaults;

		vmraid.ui.py_date_format = vmraid.boot.sysdefaults.date_format.replace('dd', '%d').replace('mm', '%m').replace('yyyy', '%Y');
		vmraid.boot.user.last_selected_values = {};

		// Proxy for user globals
		Object.defineProperties(window, {
			'user': {
				get: function() {
					console.warn('Please use `vmraid.session.user` instead of `user`. It will be deprecated soon.');
					return vmraid.session.user;
				}
			},
			'user_fullname': {
				get: function() {
					console.warn('Please use `vmraid.session.user_fullname` instead of `user_fullname`. It will be deprecated soon.');
					return vmraid.session.user;
				}
			},
			'user_email': {
				get: function() {
					console.warn('Please use `vmraid.session.user_email` instead of `user_email`. It will be deprecated soon.');
					return vmraid.session.user_email;
				}
			},
			'user_defaults': {
				get: function() {
					console.warn('Please use `vmraid.user_defaults` instead of `user_defaults`. It will be deprecated soon.');
					return vmraid.user_defaults;
				}
			},
			'roles': {
				get: function() {
					console.warn('Please use `vmraid.user_roles` instead of `roles`. It will be deprecated soon.');
					return vmraid.user_roles;
				}
			},
			'sys_defaults': {
				get: function() {
					console.warn('Please use `vmraid.sys_defaults` instead of `sys_defaults`. It will be deprecated soon.');
					return vmraid.user_roles;
				}
			}
		});
	}
	sync_pages() {
		// clear cached pages if timestamp is not found
		if(localStorage["page_info"]) {
			vmraid.boot.allowed_pages = [];
			var page_info = JSON.parse(localStorage["page_info"]);
			$.each(vmraid.boot.page_info, function(name, p) {
				if(!page_info[name] || (page_info[name].modified != p.modified)) {
					delete localStorage["_page:" + name];
				}
				vmraid.boot.allowed_pages.push(name);
			});
		} else {
			vmraid.boot.allowed_pages = Object.keys(vmraid.boot.page_info);
		}
		localStorage["page_info"] = JSON.stringify(vmraid.boot.page_info);
	}
	set_as_guest() {
		vmraid.session.user = 'Guest';
		vmraid.session.user_email = '';
		vmraid.session.user_fullname = 'Guest';

		vmraid.user_defaults = {};
		vmraid.user_roles = ['Guest'];
		vmraid.sys_defaults = {};
	}
	make_page_container() {
		if ($("#body").length) {
			$(".splash").remove();
			vmraid.temp_container = $("<div id='temp-container' style='display: none;'>")
				.appendTo("body");
			vmraid.container = new vmraid.views.Container();
		}
	}
	make_nav_bar() {
		// toolbar
		if(vmraid.boot && vmraid.boot.home_page!=='setup-wizard') {
			vmraid.vmraid_toolbar = new vmraid.ui.toolbar.Toolbar();
		}

	}
	logout() {
		var me = this;
		me.logged_out = true;
		return vmraid.call({
			method:'logout',
			callback: function(r) {
				if(r.exc) {
					return;
				}
				me.redirect_to_login();
			}
		});
	}
	handle_session_expired() {
		if(!vmraid.app.session_expired_dialog) {
			var dialog = new vmraid.ui.Dialog({
				title: __('Session Expired'),
				keep_open: true,
				fields: [
					{ fieldtype:'Password', fieldname:'password',
						label: __('Please Enter Your Password to Continue') },
				],
				onhide: () => {
					if (!dialog.logged_in) {
						vmraid.app.redirect_to_login();
					}
				}
			});
			dialog.set_primary_action(__('Login'), () => {
				dialog.set_message(__('Authenticating...'));
				vmraid.call({
					method: 'login',
					args: {
						usr: vmraid.session.user,
						pwd: dialog.get_values().password
					},
					callback: (r) => {
						if (r.message==='Logged In') {
							dialog.logged_in = true;

							// revert backdrop
							$('.modal-backdrop').css({
								'opacity': '',
								'background-color': '#334143'
							});
						}
						dialog.hide();
					},
					statusCode: () => {
						dialog.hide();
					}
				});
			});
			vmraid.app.session_expired_dialog = dialog;
		}
		if(!vmraid.app.session_expired_dialog.display) {
			vmraid.app.session_expired_dialog.show();
			// add backdrop
			$('.modal-backdrop').css({
				'opacity': 1,
				'background-color': '#4B4C9D'
			});
		}
	}
	redirect_to_login() {
		window.location.href = '/';
	}
	set_favicon() {
		var link = $('link[type="image/x-icon"]').remove().attr("href");
		$('<link rel="shortcut icon" href="' + link + '" type="image/x-icon">').appendTo("head");
		$('<link rel="icon" href="' + link + '" type="image/x-icon">').appendTo("head");
	}
	trigger_primary_action() {
		// to trigger change event on active input before triggering primary action
		$(document.activeElement).blur();
		// wait for possible JS validations triggered after blur (it might change primary button)
		setTimeout(() => {
			if (window.cur_dialog && cur_dialog.display) {
				// trigger primary
				cur_dialog.get_primary_btn().trigger("click");
			} else if (cur_frm && cur_frm.page.btn_primary.is(':visible')) {
				cur_frm.page.btn_primary.trigger('click');
			} else if (vmraid.container.page.save_action) {
				vmraid.container.page.save_action();
			}
		}, 100);
	}

	set_rtl() {
		if (vmraid.utils.is_rtl()) {
			var ls = document.createElement('link');
			ls.rel="stylesheet";
			ls.type = "text/css";
			ls.href= vmraid.assets.bundled_asset("vmraid-rtl.bundle.css");
			document.getElementsByTagName('head')[0].appendChild(ls);
			$('body').addClass('vmraid-rtl');
		}
	}

	show_change_log() {
		var me = this;
		let change_log = vmraid.boot.change_log;

		// vmraid.boot.change_log = [{
		// 	"change_log": [
		// 		[<version>, <change_log in markdown>],
		// 		[<version>, <change_log in markdown>],
		// 	],
		// 	"description": "ERP made simple",
		// 	"title": "ERPAdda",
		// 	"version": "12.2.0"
		// }];

		if (!Array.isArray(change_log) || !change_log.length || window.Cypress) {
			return;
		}

		// Iterate over changelog
		var change_log_dialog = vmraid.msgprint({
			message: vmraid.render_template("change_log", {"change_log": change_log}),
			title: __("Updated To A New Version 🎉"),
			wide: true,
		});
		change_log_dialog.keep_open = true;
		change_log_dialog.custom_onhide = function() {
			vmraid.call({
				"method": "vmraid.utils.change_log.update_last_known_versions"
			});
			me.show_notes();
		};
	}

	show_update_available() {
		vmraid.call({
			"method": "vmraid.utils.change_log.show_update_popup"
		});
	}

	setup_analytics() {
		if(window.mixpanel) {
			window.mixpanel.identify(vmraid.session.user);
			window.mixpanel.people.set({
				"$first_name": vmraid.boot.user.first_name,
				"$last_name": vmraid.boot.user.last_name,
				"$created": vmraid.boot.user.creation,
				"$email": vmraid.session.user
			});
		}
	}

	add_browser_class() {
		$('html').addClass(vmraid.utils.get_browser().name.toLowerCase());
	}

	set_fullwidth_if_enabled() {
		vmraid.ui.toolbar.set_fullwidth_if_enabled();
	}

	show_notes() {
		var me = this;
		if(vmraid.boot.notes.length) {
			vmraid.boot.notes.forEach(function(note) {
				if(!note.seen || note.notify_on_every_login) {
					var d = vmraid.msgprint({message:note.content, title:note.title});
					d.keep_open = true;
					d.custom_onhide = function() {
						note.seen = true;

						// Mark note as read if the Notify On Every Login flag is not set
						if (!note.notify_on_every_login) {
							vmraid.call({
								method: "vmraid.desk.doctype.note.note.mark_as_seen",
								args: {
									note: note.name
								}
							});
						}

						// next note
						me.show_notes();

					};
				}
			});
		}
	}

	setup_build_events() {
		if (vmraid.boot.developer_mode) {
			vmraid.require("build_events.bundle.js");
		}
	}

	setup_energy_point_listeners() {
		vmraid.realtime.on('energy_point_alert', (message) => {
			vmraid.show_alert(message);
		});
	}

	setup_copy_doc_listener() {
		$('body').on('paste', (e) => {
			try {
				let pasted_data = vmraid.utils.get_clipboard_data(e);
				let doc = JSON.parse(pasted_data);
				if (doc.doctype) {
					e.preventDefault();
					let sleep = (time) => {
						return new Promise((resolve) => setTimeout(resolve, time));
					};

					vmraid.dom.freeze(__('Creating {0}', [doc.doctype]) + '...');
					// to avoid abrupt UX
					// wait for activity feedback
					sleep(500).then(() => {
						let res = vmraid.model.with_doctype(doc.doctype, () => {
							let newdoc = vmraid.model.copy_doc(doc);
							newdoc.__newname = doc.name;
							delete doc.name;
							newdoc.idx = null;
							newdoc.__run_link_triggers = false;
							vmraid.set_route('Form', newdoc.doctype, newdoc.name);
							vmraid.dom.unfreeze();
						});
						res && res.fail(vmraid.dom.unfreeze);
					});
				}
			} catch (e) {
				//
			}
		});
	}
}

vmraid.get_module = function(m, default_module) {
	var module = vmraid.modules[m] || default_module;
	if (!module) {
		return;
	}

	if(module._setup) {
		return module;
	}

	if(!module.label) {
		module.label = m;
	}

	if(!module._label) {
		module._label = __(module.label);
	}

	module._setup = true;

	return module;
};
