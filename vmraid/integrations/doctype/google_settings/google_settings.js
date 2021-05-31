// Copyright (c) 2019, VMRaid Technologies and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Google Settings', {
	refresh: function(frm) {
		frm.dashboard.set_headline(__("For more information, {0}.", [`<a href='https://erpadda.com/docs/user/manual/en/erpadda_integration/google_settings'>${__('Click here')}</a>`]));
	}
});
