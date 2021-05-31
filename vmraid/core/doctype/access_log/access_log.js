// Copyright (c) 2019, VMRaid Technologies and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Access Log', {
	show_document: function (frm) {
		vmraid.set_route('Form', frm.doc.export_from, frm.doc.reference_document);
	},

	show_report: function (frm) {
		if (frm.doc.report_name.includes('/')) {
			vmraid.set_route(frm.doc.report_name);
		} else {
			let filters = frm.doc.filters ? JSON.parse(frm.doc.filters) : {};
			vmraid.set_route('query-report', frm.doc.report_name, filters);
		}
	}
});
