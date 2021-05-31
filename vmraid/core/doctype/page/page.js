// Copyright (c) 2016, VMRaid Technologies and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Page', {
	refresh: function(frm) {
		if (!vmraid.boot.developer_mode && vmraid.session.user != 'Administrator') {
			// make the document read-only
			frm.set_read_only();
		}
		if (!frm.is_new() && !frm.doc.istable) {
			frm.add_custom_button(__('Go to {0} Page', [frm.doc.title || frm.doc.name]), () => {
				vmraid.set_route(frm.doc.name);
			});
		}
	}
});
