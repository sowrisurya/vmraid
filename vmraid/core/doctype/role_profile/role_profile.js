// Copyright (c) 2017, VMRaid Technologies and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Role Profile', {
	refresh: function(frm) {
		if (has_common(vmraid.user_roles, ["Administrator", "System Manager"])) {
			if (!frm.roles_editor) {
				const role_area = $(frm.fields_dict.roles_html.wrapper);
				frm.roles_editor = new vmraid.RoleEditor(role_area, frm);
			}
			frm.roles_editor.show();

		}
	},

	validate: function(frm) {
		if (frm.roles_editor) {
			frm.roles_editor.set_roles_in_table();
		}
	}
});
