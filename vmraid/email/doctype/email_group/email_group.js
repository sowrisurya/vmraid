// Copyright (c) 2016, VMRaid Technologies and contributors
// For license information, please see license.txt

vmraid.ui.form.on("Email Group", "refresh", function(frm) {
	if(!frm.is_new()) {
		frm.add_custom_button(__("Import Subscribers"), function() {
			vmraid.prompt({fieldtype:"Select", options: frm.doc.__onload.import_types,
				label:__("Import Email From"), fieldname:"doctype", reqd:1},
				function(data) {
					vmraid.call({
						method: "vmraid.email.doctype.email_group.email_group.import_from",
						args: {
							"name": frm.doc.name,
							"doctype": data.doctype
						},
						callback: function(r) {
							frm.set_value("total_subscribers", r.message);
						}
					})
				}, __("Import Subscribers"), __("Import"));
		}, __("Action"));

		frm.add_custom_button(__("Add Subscribers"), function() {
			vmraid.prompt({fieldtype:"Text",
				label:__("Email Addresses"), fieldname:"email_list", reqd:1},
				function(data) {
					vmraid.call({
						method: "vmraid.email.doctype.email_group.email_group.add_subscribers",
						args: {
							"name": frm.doc.name,
							"email_list": data.email_list
						},
						callback: function(r) {
							frm.set_value("total_subscribers", r.message);
						}
					})
				}, __("Add Subscribers"), __("Add"));
		}, __("Action"));

		frm.add_custom_button(__("New Newsletter"), function() {
			vmraid.route_options = {"email_group": frm.doc.name};
			vmraid.new_doc("Newsletter");
		}, __("Action"));

	}
});
