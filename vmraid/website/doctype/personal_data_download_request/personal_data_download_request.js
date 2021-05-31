// Copyright (c) 2019, VMRaid Technologies and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Personal Data Download Request', {
	onload: function(frm) {
		if (frm.is_new()) {
			frm.doc.user = vmraid.session.user;
		}
	},
});
