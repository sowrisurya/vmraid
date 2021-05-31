// Copyright (c) 2017, VMRaid Technologies and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Print Style', {
	refresh: function(frm) {
		frm.add_custom_button(__('Print Settings'), () => {
			vmraid.set_route('Form', 'Print Settings');
		})
	}
});
