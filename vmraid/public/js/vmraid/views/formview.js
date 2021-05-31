// Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vmraid.provide('vmraid.views.formview');

vmraid.views.FormFactory = class FormFactory extends vmraid.views.Factory {
	make(route) {
		var doctype = route[1],
			doctype_layout = vmraid.router.doctype_layout || doctype;

		if (!vmraid.views.formview[doctype_layout]) {
			vmraid.model.with_doctype(doctype, () => {
				this.page = vmraid.container.add_page(doctype_layout);
				vmraid.views.formview[doctype_layout] = this.page;
				this.make_and_show(doctype, route);
			});
		} else {
			this.show_doc(route);
		}

		this.setup_events();
	}

	make_and_show(doctype, route) {
		if (vmraid.router.doctype_layout) {
			vmraid.model.with_doc('DocType Layout', vmraid.router.doctype_layout, () => {
				this.make_form(doctype);
				this.show_doc(route);
			});
		} else {
			this.make_form(doctype);
			this.show_doc(route);
		}
	}

	make_form(doctype) {
		this.page.frm = new vmraid.ui.form.Form(doctype, this.page, true, vmraid.router.doctype_layout);
	}

	setup_events() {
		if (!this.initialized) {
			$(document).on("page-change", function() {
				vmraid.ui.form.close_grid_form();
			});

			vmraid.realtime.on("doc_viewers", function(data) {
				// set users that currently viewing the form
				vmraid.ui.form.FormViewers.set_users(data, 'viewers');
			});

			vmraid.realtime.on("doc_typers", function(data) {
				// set users that currently typing on the form
				vmraid.ui.form.FormViewers.set_users(data, 'typers');
			});
		}
		this.initialized = true;
	}

	show_doc(route) {
		var doctype = route[1],
			doctype_layout = vmraid.router.doctype_layout || doctype,
			name = route.slice(2).join("/");

		if (vmraid.model.new_names[name]) {
			// document has been renamed, reroute
			name = vmraid.model.new_names[name];
			vmraid.set_route("Form", doctype_layout, name);
			return;
		}

		const doc = vmraid.get_doc(doctype, name);
		if (doc && vmraid.model.get_docinfo(doctype, name) && (doc.__islocal || vmraid.model.is_fresh(doc))) {
			// is document available and recent?
			this.render(doctype_layout, name);
		} else {
			this.fetch_and_render(doctype, name, doctype_layout);
		}
	}

	fetch_and_render(doctype, name, doctype_layout) {
		vmraid.model.with_doc(doctype, name, (name, r) => {
			if (r && r['403']) return; // not permitted

			if (!(locals[doctype] && locals[doctype][name])) {
				if (name && name.substr(0, 3) === 'new') {
					this.render_new_doc(doctype, name, doctype_layout);
				} else {
					vmraid.show_not_found();
				}
				return;
			}
			this.render(doctype_layout, name);
		});
	}

	render_new_doc(doctype, name, doctype_layout) {
		const new_name = vmraid.model.make_new_doc_and_get_name(doctype, true);
		if (new_name===name) {
			this.render(doctype_layout, name);
		} else {
			vmraid.set_route("Form", doctype_layout, new_name);
		}
	}

	render(doctype_layout, name) {
		vmraid.container.change_to(doctype_layout);
		vmraid.views.formview[doctype_layout].frm.refresh(name);
	}
}
