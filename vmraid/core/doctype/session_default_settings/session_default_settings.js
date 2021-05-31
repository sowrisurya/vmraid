// Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vmraid.ui.form.on('Session Default Settings', {
	refresh: function(frm) {
		frm.set_query('ref_doctype', 'session_defaults', function() {
			return {
				filters: {
					issingle: 0,
					istable: 0
				}
			};
		});
	}
});
