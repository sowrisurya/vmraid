vmraid.provide('vmraid.ui.form');

vmraid.quick_edit = function(doctype, name) {
	vmraid.db.get_doc(doctype, name).then(doc => {
		vmraid.ui.form.make_quick_entry(doctype, null, null, doc);
	});
};

vmraid.ui.form.make_quick_entry = (doctype, after_insert, init_callback, doc, force) => {
	var trimmed_doctype = doctype.replace(/ /g, '');
	var controller_name = "QuickEntryForm";

	if(vmraid.ui.form[trimmed_doctype + "QuickEntryForm"]){
		controller_name = trimmed_doctype + "QuickEntryForm";
	}

	vmraid.quick_entry = new vmraid.ui.form[controller_name](doctype, after_insert, init_callback, doc, force);
	return vmraid.quick_entry.setup();
};

vmraid.ui.form.QuickEntryForm = class QuickEntryForm {
	constructor(doctype, after_insert, init_callback, doc, force) {
		this.doctype = doctype;
		this.after_insert = after_insert;
		this.init_callback = init_callback;
		this.doc = doc;
		this.force = force ? force : false;
	}

	setup() {
		return new Promise(resolve => {
			vmraid.model.with_doctype(this.doctype, () => {
				this.check_quick_entry_doc();
				this.set_meta_and_mandatory_fields();
				if (this.is_quick_entry() || this.force) {
					this.render_dialog();
					resolve(this);
				} else {
					// no quick entry, open full form
					vmraid.quick_entry = null;
					vmraid.set_route('Form', this.doctype, this.doc.name)
						.then(() => resolve(this));
					// call init_callback for consistency
					if (this.init_callback) {
						this.init_callback(this.doc);
					}
				}
			});
		});
	}

	set_meta_and_mandatory_fields() {
		this.meta = vmraid.get_meta(this.doctype);
		let fields = this.meta.fields;

		// prepare a list of mandatory, bold and allow in quick entry fields
		this.mandatory = fields.filter(df => {
			return ((df.reqd || df.bold || df.allow_in_quick_entry) && !df.read_only);
		});
	}

	check_quick_entry_doc() {
		if (!this.doc) {
			this.doc = vmraid.model.get_new_doc(this.doctype, null, null, true);
		}
	}

	is_quick_entry() {
		if(this.meta.quick_entry != 1) {
			return false;
		}

		this.validate_for_prompt_autoname();

		if (this.has_child_table() || !this.mandatory.length) {
			return false;
		}

		return true;
	}

	too_many_mandatory_fields() {
		if(this.mandatory.length > 7) {
			// too many fields, show form
			return true;
		}
		return false;
	}

	has_child_table(){
		if($.map(this.mandatory, function(d) {
			return d.fieldtype==='Table' ? d : null; }).length) {
			// has mandatory table, quit!
			return true;
		}
		return false;
	}

	validate_for_prompt_autoname() {
		if(this.meta.autoname && this.meta.autoname.toLowerCase()==='prompt') {
			this.mandatory = [{fieldname:'__newname', label:__('{0} Name', [this.meta.name]),
				reqd: 1, fieldtype:'Data'}].concat(this.mandatory);
		}
	}

	render_dialog() {
		var me = this;
		this.dialog = new vmraid.ui.Dialog({
			title: __("New {0}", [__(this.doctype)]),
			fields: this.mandatory,
			doc: this.doc
		});

		this.register_primary_action();
		!this.force && this.render_edit_in_full_page_link();
		// ctrl+enter to save
		this.dialog.wrapper.keydown(function(e) {
			if((e.ctrlKey || e.metaKey) && e.which==13) {
				if(!vmraid.request.ajax_count) {
					// not already working -- double entry
					me.dialog.get_primary_btn().trigger("click");
					e.preventDefault();
					return false;
				}
			}
		});

		this.dialog.onhide = () => vmraid.quick_entry = null;
		this.dialog.show();

		this.dialog.refresh_dependency();
		this.set_defaults();

		if (this.init_callback) {
			this.init_callback(this.dialog);
		}
	}

	register_primary_action() {
		var me = this;
		this.dialog.set_primary_action(__('Save'), function() {
			if(me.dialog.working) {
				return;
			}
			var data = me.dialog.get_values();

			if(data) {
				me.dialog.working = true;
				me.dialog.set_message(__('Saving...'));
				me.insert().then(() => {
					me.dialog.clear_message();
				});
			}
		});
	}

	insert() {
		let me = this;
		return new Promise(resolve => {
			me.update_doc();
			vmraid.call({
				method: "vmraid.client.save",
				args: {
					doc: me.dialog.doc
				},
				callback: function(r) {

					if (vmraid.model.is_submittable(me.doctype)) {
						vmraid.run_serially([
							() => me.dialog.working = true,
							() => {
								me.dialog.set_primary_action(__('Submit'), function() {
									me.submit(r.message);
								});
							}
						]);
					} else {
						me.dialog.hide();
						// delete the old doc
						vmraid.model.clear_doc(me.dialog.doc.doctype, me.dialog.doc.name);
						me.dialog.doc = r.message;
						if(vmraid._from_link) {
							vmraid.ui.form.update_calling_link(me.dialog.doc);
						} else {
							if(me.after_insert) {
								me.after_insert(me.dialog.doc);
							} else {
								me.open_form_if_not_list();
							}
						}
					}
				},
				error: function() {
					if (!me.skip_redirect_on_error) {
						me.open_doc(true);
					}
				},
				always: function() {
					me.dialog.working = false;
					resolve(me.dialog.doc);
				},
				freeze: true
			});
		});
	}

	submit(doc) {
		var me = this;
		vmraid.call({
			method: "vmraid.client.submit",
			args : {
				doc: doc
			},
			callback: function(r) {
				me.dialog.hide();
				// delete the old doc
				vmraid.model.clear_doc(me.dialog.doc.doctype, me.dialog.doc.name);
				me.dialog.doc = r.message;
				if (vmraid._from_link) {
					vmraid.ui.form.update_calling_link(me.dialog.doc);
				} else {
					if (me.after_insert) {
						me.after_insert(me.dialog.doc);
					} else {
						me.open_form_if_not_list();
					}
				}

				cur_frm && cur_frm.reload_doc();
			}
		});
	}

	open_form_if_not_list() {
		let route = vmraid.get_route();
		let doc = this.dialog.doc;
		if (route && !(route[0]==='List' && route[1]===doc.doctype)) {
			vmraid.run_serially([
				() => vmraid.set_route('Form', doc.doctype, doc.name)
			]);
		}
	}

	update_doc(){
		var me = this;
		var data = this.dialog.get_values(true);
		$.each(data, function(key, value) {
			if (!is_null(value)) {
				me.dialog.doc[key] = value;
			}
		});
		return this.dialog.doc;
	}

	open_doc(set_hooks) {
		this.dialog.hide();
		this.update_doc();
		if (set_hooks && this.after_insert) {
			vmraid.route_options = vmraid.route_options || {};
			vmraid.route_options.after_save = (frm) => {
				this.after_insert(frm);
			};
		}
		vmraid.set_route('Form', this.doctype, this.doc.name);
	}

	render_edit_in_full_page_link() {
		var me = this;
		this.dialog.add_custom_action(
			`${vmraid.utils.icon('edit', 'xs')} ${__("Edit in full page")}`,
			() => me.open_doc(true)
		);
	}

	set_defaults() {
		var me = this;
		// set defaults
		$.each(this.dialog.fields_dict, function(fieldname, field) {
			field.doctype = me.doc.doctype;
			field.docname = me.doc.name;

			if (!is_null(me.doc[fieldname])) {
				field.set_input(me.doc[fieldname]);
			}
		});
	}
};
