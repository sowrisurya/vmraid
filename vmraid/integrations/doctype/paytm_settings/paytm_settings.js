// Copyright (c) 2020, VMRaid Technologies and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Paytm Settings', {
	refresh: function(frm) {
		frm.dashboard.set_headline(__("For more information, {0}.", [`<a href='https://erpadda.com/docs/user/manual/en/erpadda_integration/paytm-integration'>${__('Click here')}</a>`]));
	}
});
