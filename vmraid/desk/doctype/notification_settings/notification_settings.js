// Copyright (c) 2019, VMRaid Technologies and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Notification Settings', {
	onload: (frm) => {
		vmraid.breadcrumbs.add({
			label: __('Settings'),
			route: '#modules/Settings',
			type: 'Custom'
		});
		frm.set_query('subscribed_documents', () => {
			return {
				filters: {
					istable: 0
				}
			};
		});
	},

	refresh: (frm) => {
		if (vmraid.user.has_role('System Manager')) {
			frm.add_custom_button(__('Go to Notification Settings List'), () => {
				vmraid.set_route('List', 'Notification Settings');
			});
		}
	}

});
