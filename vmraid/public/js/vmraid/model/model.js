// Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vmraid.provide('vmraid.model');

$.extend(vmraid.model, {
	no_value_type: ['Section Break', 'Column Break', 'HTML', 'Table', 'Table MultiSelect',
		'Button', 'Image', 'Fold', 'Heading'],

	layout_fields: ['Section Break', 'Column Break', 'Fold'],

	std_fields_list: ['name', 'owner', 'creation', 'modified', 'modified_by',
		'_user_tags', '_comments', '_assign', '_liked_by', 'docstatus',
		'parent', 'parenttype', 'parentfield', 'idx'],

	core_doctypes_list: ['DocType', 'DocField', 'DocPerm', 'User', 'Role', 'Has Role',
		'Page', 'Module Def', 'Print Format', 'Report', 'Customize Form',
		'Customize Form Field', 'Property Setter', 'Custom Field', 'Client Script'],

	std_fields: [
		{fieldname:'name', fieldtype:'Link', label:__('ID')},
		{fieldname:'owner', fieldtype:'Link', label:__('Created By'), options: 'User'},
		{fieldname:'idx', fieldtype:'Int', label:__('Index')},
		{fieldname:'creation', fieldtype:'Date', label:__('Created On')},
		{fieldname:'modified', fieldtype:'Date', label:__('Last Updated On')},
		{fieldname:'modified_by', fieldtype:'Data', label:__('Last Updated By')},
		{fieldname:'_user_tags', fieldtype:'Data', label:__('Tags')},
		{fieldname:'_liked_by', fieldtype:'Data', label:__('Liked By')},
		{fieldname:'_comments', fieldtype:'Text', label:__('Comments')},
		{fieldname:'_assign', fieldtype:'Text', label:__('Assigned To')},
		{fieldname:'docstatus', fieldtype:'Int', label:__('Document Status')},
	],

	numeric_fieldtypes: ["Int", "Float", "Currency", "Percent", "Duration"],

	std_fields_table: [
		{fieldname:'parent', fieldtype:'Data', label:__('Parent')},
	],

	table_fields: ['Table', 'Table MultiSelect'],

	new_names: {},
	events: {},
	user_settings: {},

	init: function() {
		// setup refresh if the document is updated somewhere else
		vmraid.realtime.on("doc_update", function(data) {
			// set list dirty
			vmraid.views.ListView.trigger_list_update(data);
			var doc = locals[data.doctype] && locals[data.doctype][data.name];

			if(doc) {
				// current document is dirty, show message if its not me
				if(vmraid.get_route()[0]==="Form" && cur_frm.doc.doctype===doc.doctype && cur_frm.doc.name===doc.name) {
					if(!vmraid.ui.form.is_saving && data.modified!=cur_frm.doc.modified) {
						doc.__needs_refresh = true;
						cur_frm.check_doctype_conflict();
					}
				} else {
					if(!doc.__unsaved) {
						// no local changes, remove from locals
						vmraid.model.remove_from_locals(doc.doctype, doc.name);
					} else {
						// show message when user navigates back
						doc.__needs_refresh = true;
					}
				}
			}
		});

		vmraid.realtime.on("list_update", function(data) {
			vmraid.views.ListView.trigger_list_update(data);
		});

	},

	is_value_type: function(fieldtype) {
		if (typeof fieldtype == 'object') {
			fieldtype = fieldtype.fieldtype;
		}
		// not in no-value type
		return vmraid.model.no_value_type.indexOf(fieldtype)===-1;
	},

	is_non_std_field: function(fieldname) {
		return !vmraid.model.std_fields_list.includes(fieldname);
	},

	get_std_field: function(fieldname, ignore=false) {
		var docfield = $.map([].concat(vmraid.model.std_fields).concat(vmraid.model.std_fields_table),
			function(d) {
				if(d.fieldname==fieldname) return d;
			});
		if (!docfield.length) {
			//Standard fields are ignored in case of adding columns as a result of groupby
			if (ignore) {
				return {fieldname: fieldname};
			} else {
				vmraid.msgprint(__("Unknown Column: {0}", [fieldname]));
			}
		}
		return docfield[0];
	},

	get_from_localstorage: function(doctype) {
		if (localStorage["_doctype:" + doctype]) {
			return JSON.parse(localStorage["_doctype:" + doctype]);
		}
	},

	set_in_localstorage: function(doctype, docs) {
		try {
			localStorage["_doctype:" + doctype] = JSON.stringify(docs);
		} catch(e) {
			// if quota is exceeded, clear local storage and set item
			console.warn("localStorage quota exceeded, clearing doctype cache")
			vmraid.model.clear_local_storage();
			localStorage["_doctype:" + doctype] = JSON.stringify(docs);
		}
	},

	clear_local_storage: function() {
		for(var key in localStorage) {
			if (key.startsWith("_doctype:")) {
				localStorage.removeItem(key);
			}
		}
	},

	with_doctype: function(doctype, callback, async) {
		if(locals.DocType[doctype]) {
			callback && callback();
		} else {
			let cached_timestamp = null;
			let cached_doc = null;

			let cached_docs = vmraid.model.get_from_localstorage(doctype);

			if (cached_docs) {
				cached_doc = cached_docs.filter(doc => doc.name === doctype)[0];
				if(cached_doc) {
					cached_timestamp = cached_doc.modified;
				}
			}

			return vmraid.call({
				method:'vmraid.desk.form.load.getdoctype',
				type: "GET",
				args: {
					doctype: doctype,
					with_parent: 1,
					cached_timestamp: cached_timestamp
				},
				async: async,
				callback: function(r) {
					if(r.exc) {
						vmraid.msgprint(__("Unable to load: {0}", [__(doctype)]));
						throw "No doctype";
					}
					if(r.message=="use_cache") {
						vmraid.model.sync(cached_doc);
					} else {
						vmraid.model.set_in_localstorage(doctype, r.docs)
					}
					vmraid.model.init_doctype(doctype);

					if(r.user_settings) {
						// remember filters and other settings from last view
						vmraid.model.user_settings[doctype] = JSON.parse(r.user_settings);
						vmraid.model.user_settings[doctype].updated_on = moment().toString();
					}
					callback && callback(r);
				}
			});
		}
	},

	init_doctype: function(doctype) {
		var meta = locals.DocType[doctype];
		if(meta.__list_js) {
			eval(meta.__list_js);
		}
		if(meta.__custom_list_js) {
			eval(meta.__custom_list_js);
		}
		if(meta.__calendar_js) {
			eval(meta.__calendar_js);
		}
		if(meta.__map_js) {
			eval(meta.__map_js);
		}
		if(meta.__tree_js) {
			eval(meta.__tree_js);
		}
		if(meta.__templates) {
			$.extend(vmraid.templates, meta.__templates);
		}
	},

	with_doc: function(doctype, name, callback) {
		return new Promise(resolve => {
			if(!name) name = doctype; // single type
			if(locals[doctype] && locals[doctype][name] && vmraid.model.get_docinfo(doctype, name)) {
				callback && callback(name);
				resolve(vmraid.get_doc(doctype, name));
			} else {
				return vmraid.call({
					method: 'vmraid.desk.form.load.getdoc',
					type: "GET",
					args: {
						doctype: doctype,
						name: name
					},
					callback: function(r) {
						callback && callback(name, r);
						resolve(vmraid.get_doc(doctype, name));
					}
				});
			}
		});
	},

	get_docinfo: function(doctype, name) {
		return vmraid.model.docinfo[doctype] && vmraid.model.docinfo[doctype][name] || null;
	},

	set_docinfo: function(doctype, name, key, value) {
		if (vmraid.model.docinfo[doctype] && vmraid.model.docinfo[doctype][name]) {
			vmraid.model.docinfo[doctype][name][key] = value;
		}
	},

	get_shared: function(doctype, name) {
		return vmraid.model.get_docinfo(doctype, name).shared;
	},

	get_server_module_name: function(doctype) {
		var dt = vmraid.model.scrub(doctype);
		var module = vmraid.model.scrub(locals.DocType[doctype].module);
		var app = vmraid.boot.module_app[module];
		return app + "." + module + '.doctype.' + dt + '.' + dt;
	},

	scrub: function(txt) {
		return txt.replace(/ /g, "_").toLowerCase();  // use to slugify or create a slug, a "code-friendly" string
	},

	unscrub: function(txt) {
		return __(txt || '').replace(/-|_/g, " ").replace(/\w*/g,
            function(keywords){return keywords.charAt(0).toUpperCase() + keywords.substr(1).toLowerCase();});
	},

	can_create: function(doctype) {
		return vmraid.boot.user.can_create.indexOf(doctype)!==-1;
	},

	can_select: function(doctype) {
		if (vmraid.boot.user) {
			return vmraid.boot.user.can_select.indexOf(doctype)!==-1;
		}
	},

	can_read: function(doctype) {
		if (vmraid.boot.user) {
			return vmraid.boot.user.can_read.indexOf(doctype)!==-1;
		}
	},

	can_write: function(doctype) {
		return vmraid.boot.user.can_write.indexOf(doctype)!==-1;
	},

	can_get_report: function(doctype) {
		return vmraid.boot.user.can_get_report.indexOf(doctype)!==-1;
	},

	can_delete: function(doctype) {
		if(!doctype) return false;
		return vmraid.boot.user.can_delete.indexOf(doctype)!==-1;
	},

	can_cancel: function(doctype) {
		if(!doctype) return false;
		return vmraid.boot.user.can_cancel.indexOf(doctype)!==-1;
	},

	has_workflow: function(doctype) {
		return vmraid.get_list('Workflow', {'document_type': doctype,
			'is_active': 1}).length;
	},

	is_submittable: function(doctype) {
		if(!doctype) return false;
		return locals.DocType[doctype]
			&& locals.DocType[doctype].is_submittable;
	},

	is_table: function(doctype) {
		if(!doctype) return false;
		return locals.DocType[doctype] && locals.DocType[doctype].istable;
	},

	is_single: function(doctype) {
		if(!doctype) return false;
		return vmraid.boot.single_types.indexOf(doctype) != -1;
	},

	is_tree: function(doctype) {
		if (!doctype) return false;
		return vmraid.boot.treeviews.indexOf(doctype) != -1;
	},

	is_fresh(doc) {
		// returns true if document has been recently loaded (5 seconds ago)
		return doc && doc.__last_sync_on && ((new Date() - doc.__last_sync_on)) < 5000;
	},

	can_import: function(doctype, frm) {
		// system manager can always import
		if(vmraid.user_roles.includes("System Manager")) return true;

		if(frm) return frm.perm[0].import===1;
		return vmraid.boot.user.can_import.indexOf(doctype)!==-1;
	},

	can_export: function(doctype, frm) {
		// system manager can always export
		if(vmraid.user_roles.includes("System Manager")) return true;

		if(frm) return frm.perm[0].export===1;
		return vmraid.boot.user.can_export.indexOf(doctype)!==-1;
	},

	can_print: function(doctype, frm) {
		if(frm) return frm.perm[0].print===1;
		return vmraid.boot.user.can_print.indexOf(doctype)!==-1;
	},

	can_email: function(doctype, frm) {
		if(frm) return frm.perm[0].email===1;
		return vmraid.boot.user.can_email.indexOf(doctype)!==-1;
	},

	can_share: function(doctype, frm) {
		if(frm) {
			return frm.perm[0].share===1;
		}
		return vmraid.boot.user.can_share.indexOf(doctype)!==-1;
	},

	can_set_user_permissions: function(doctype, frm) {
		// system manager can always set user permissions
		if(vmraid.user_roles.includes("System Manager")) return true;

		if(frm) return frm.perm[0].set_user_permissions===1;
		return vmraid.boot.user.can_set_user_permissions.indexOf(doctype)!==-1;
	},

	has_value: function(dt, dn, fn) {
		// return true if property has value
		var val = locals[dt] && locals[dt][dn] && locals[dt][dn][fn];
		var df = vmraid.meta.get_docfield(dt, fn, dn);

		if(vmraid.model.table_fields.includes(df.fieldtype)) {
			var ret = false;
			$.each(locals[df.options] || {}, function(k,d) {
				if(d.parent==dn && d.parenttype==dt && d.parentfield==df.fieldname) {
					ret = true;
					return false;
				}
			});
		} else {
			var ret = !is_null(val);
		}
		return ret ? true : false;
	},

	get_list: function(doctype, filters) {
		var docsdict = locals[doctype] || locals[":" + doctype] || {};
		if($.isEmptyObject(docsdict))
			return [];
		return vmraid.utils.filter_dict(docsdict, filters);
	},

	get_value: function(doctype, filters, fieldname, callback) {
		if(callback) {
			vmraid.call({
				method:"vmraid.client.get_value",
				args: {
					doctype: doctype,
					fieldname: fieldname,
					filters: filters
				},
				callback: function(r) {
					if(!r.exc) {
						callback(r.message);
					}
				}
			});
		} else {
			if(typeof filters==="string" && locals[doctype] && locals[doctype][filters]) {
				return locals[doctype][filters][fieldname];
			} else {
				var l = vmraid.get_list(doctype, filters);
				return (l.length && l[0]) ? l[0][fieldname] : null;
			}
		}
	},

	set_value: function(doctype, docname, fieldname, value, fieldtype) {
		/* help: Set a value locally (if changed) and execute triggers */

		var doc;
		if ($.isPlainObject(doctype)) {
			// first parameter is the doc, shift parameters to the left
			doc = doctype; fieldname = docname; value = fieldname;
		} else {
			doc = locals[doctype] && locals[doctype][docname];
		}

		let to_update = fieldname;
		let tasks = [];
		if(!$.isPlainObject(to_update)) {
			to_update = {};
			to_update[fieldname] = value;
		}

		$.each(to_update, (key, value) => {
			if (doc && doc[key] !== value) {
				if(doc.__unedited && !(!doc[key] && !value)) {
					// unset unedited flag for virgin rows
					doc.__unedited = false;
				}

				doc[key] = value;
				tasks.push(() => vmraid.model.trigger(key, value, doc));
			} else {
				// execute link triggers (want to reselect to execute triggers)
				if(in_list(["Link", "Dynamic Link"], fieldtype) && doc) {
					tasks.push(() => vmraid.model.trigger(key, value, doc));
				}
			}
		});

		return vmraid.run_serially(tasks);
	},

	on: function(doctype, fieldname, fn) {
		/* help: Attach a trigger on change of a particular field.
		To trigger on any change in a particular doctype, use fieldname as "*"
		*/
		/* example: vmraid.model.on("Customer", "age", function(fieldname, value, doc) {
		  if(doc.age < 16) {
		   	vmraid.msgprint("Warning, Customer must atleast be 16 years old.");
		    raise "CustomerAgeError";
		  }
		}) */
		vmraid.provide("vmraid.model.events." + doctype);
		if(!vmraid.model.events[doctype][fieldname]) {
			vmraid.model.events[doctype][fieldname] = [];
		}
		vmraid.model.events[doctype][fieldname].push(fn);
	},

	trigger: function(fieldname, value, doc) {
		let tasks = [];
		var runner = function(events, event_doc) {
			$.each(events || [], function(i, fn) {
				if(fn) {
					let _promise = fn(fieldname, value, event_doc || doc);

					// if the trigger returns a promise, return it,
					// or use the default promise vmraid.after_ajax
					if (_promise && _promise.then) {
						return _promise;
					} else {
						return vmraid.after_server_call();
					}
				}
			});
		};

		if(vmraid.model.events[doc.doctype]) {
			tasks.push(() => {
				return runner(vmraid.model.events[doc.doctype][fieldname]);
			});

			tasks.push(() => {
				return runner(vmraid.model.events[doc.doctype]['*']);
			});
		}

		return vmraid.run_serially(tasks);
	},

	get_doc: function(doctype, name) {
		if(!name) name = doctype;
		if($.isPlainObject(name)) {
			var doc = vmraid.get_list(doctype, name);
			return doc && doc.length ? doc[0] : null;
		}
		return locals[doctype] ? locals[doctype][name] : null;
	},

	get_children: function(doctype, parent, parentfield, filters) {
		if($.isPlainObject(doctype)) {
			var doc = doctype;
			var filters = parentfield
			var parentfield = parent;
		} else {
			var doc = vmraid.get_doc(doctype, parent);
		}

		var children = doc[parentfield] || [];
		if(filters) {
			return vmraid.utils.filter_dict(children, filters);
		} else {
			return children;
		}
	},

	clear_table: function(doc, parentfield) {
		for (var i=0, l=(doc[parentfield] || []).length; i<l; i++) {
			var d = doc[parentfield][i];
			delete locals[d.doctype][d.name];
		}
		doc[parentfield] = [];
	},

	remove_from_locals: function(doctype, name) {
		this.clear_doc(doctype, name);
		if(vmraid.views.formview[doctype]) {
			delete vmraid.views.formview[doctype].frm.opendocs[name];
		}
	},

	clear_doc: function(doctype, name) {
		var doc = locals[doctype] && locals[doctype][name];
		if(!doc) return;

		var parent = null;
		if(doc.parenttype) {
			var parent = doc.parent,
				parenttype = doc.parenttype,
				parentfield = doc.parentfield;
		}
		delete locals[doctype][name];
		if(parent) {
			var parent_doc = locals[parenttype][parent];
			var newlist = [], idx = 1;
			$.each(parent_doc[parentfield], function(i, d) {
				if(d.name!=name) {
					newlist.push(d);
					d.idx = idx;
					idx++;
				}
				parent_doc[parentfield] = newlist;
			});
		}
	},

	get_no_copy_list: function(doctype) {
		var no_copy_list = ['name','amended_from','amendment_date','cancel_reason'];

		var docfields = vmraid.get_doc("DocType", doctype).fields || [];
		for(var i=0, j=docfields.length; i<j; i++) {
			var df = docfields[i];
			if(cint(df.no_copy)) no_copy_list.push(df.fieldname);
		}

		return no_copy_list;
	},

	delete_doc: function(doctype, docname, callback) {
		var title = docname;
		var title_field = vmraid.get_meta(doctype).title_field;
		if (vmraid.get_meta(doctype).autoname == "hash" && title_field) {
			var title = vmraid.model.get_value(doctype, docname, title_field);
			title += " (" + docname + ")";
		}
		vmraid.confirm(__("Permanently delete {0}?", [title]), function() {
			return vmraid.call({
				method: 'vmraid.client.delete',
				args: {
					doctype: doctype,
					name: docname
				},
				callback: function(r, rt) {
					if(!r.exc) {
						vmraid.utils.play_sound("delete");
						vmraid.model.clear_doc(doctype, docname);
						if(callback) callback(r,rt);
					}
				}
			})
		})
	},

	rename_doc: function(doctype, docname, callback) {
			let message = __("Merge with existing");
			let warning = __("This cannot be undone");
			let merge_label = message + " <b>(" + warning + ")</b>";

		var d = new vmraid.ui.Dialog({
			title: __("Rename {0}", [__(docname)]),
			fields: [
				{label: __("New Name"), fieldname: "new_name", fieldtype: "Data", reqd: 1, "default": docname},
				{label: merge_label, fieldtype: "Check", fieldname: "merge"},
			]
		});

		d.set_primary_action(__("Rename"), function() {
			var args = d.get_values();
			if(!args) return;
			return vmraid.call({
				method:"vmraid.rename_doc",
				args: {
					doctype: doctype,
					old: docname,
					new: args.new_name,
					merge: args.merge
				},
				btn: d.get_primary_btn(),
				callback: function(r,rt) {
					if(!r.exc) {
						$(document).trigger('rename', [doctype, docname,
							r.message || args.new_name]);
						if(locals[doctype] && locals[doctype][docname])
							delete locals[doctype][docname];
						d.hide();
						if(callback)
							callback(r.message);
					}
				}
			});
		});
		d.show();
	},

	round_floats_in: function(doc, fieldnames) {
		if(!fieldnames) {
			fieldnames = vmraid.meta.get_fieldnames(doc.doctype, doc.parent,
				{"fieldtype": ["in", ["Currency", "Float"]]});
		}
		for(var i=0, j=fieldnames.length; i < j; i++) {
			var fieldname = fieldnames[i];
			doc[fieldname] = flt(doc[fieldname], precision(fieldname, doc));
		}
	},

	validate_missing: function(doc, fieldname) {
		if(!doc[fieldname]) {
			vmraid.throw(__("Please specify") + ": " +
				__(vmraid.meta.get_label(doc.doctype, fieldname, doc.parent || doc.name)));
		}
	},

	get_all_docs: function(doc) {
		var all = [doc];
		for(var key in doc) {
			if($.isArray(doc[key])) {
				var children = doc[key];
				for (var i=0, l=children.length; i < l; i++) {
					all.push(children[i]);
				}
			}
		}
		return all;
	},

	get_full_column_name: function(fieldname, doctype) {
		if (fieldname.includes('`tab')) return fieldname;
		return '`tab' + doctype + '`.`' + fieldname + '`';
	},

	is_numeric_field: function(fieldtype) {
		if (!fieldtype) return;
		if (typeof fieldtype === 'object') {
			fieldtype = fieldtype.fieldtype;
		}
		return vmraid.model.numeric_fieldtypes.includes(fieldtype);
	}
});

// legacy
vmraid.get_doc = vmraid.model.get_doc;
vmraid.get_children = vmraid.model.get_children;
vmraid.get_list = vmraid.model.get_list;

var getchildren = function(doctype, parent, parentfield) {
	var children = [];
	$.each(locals[doctype] || {}, function(i, d) {
		if(d.parent === parent && d.parentfield === parentfield) {
			children.push(d);
		}
	});
	return children;
}
