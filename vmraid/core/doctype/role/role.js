// Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vmraid.ui.form.on('Role', {
	refresh: function(frm) {
		frm.set_df_property('is_custom', 'read_only', vmraid.session.user !== 'Administrator');

		frm.add_custom_button("Role Permissions Manager", function() {
			vmraid.route_options = {"role": frm.doc.name};
			vmraid.set_route("permission-manager");
		});
		frm.add_custom_button("Show Users", function() {
			vmraid.route_options = {"role": frm.doc.name};
			vmraid.set_route("List", "User", "Report");
		});
	}
});
