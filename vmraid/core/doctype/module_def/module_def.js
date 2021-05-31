// Copyright (c) 2016, VMRaid Technologies and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Module Def', {
	refresh: function(frm) {
		vmraid.xcall('vmraid.core.doctype.module_def.module_def.get_installed_apps').then(r => {
			frm.set_df_property('app_name', 'options', JSON.parse(r));
		});
	}
});
