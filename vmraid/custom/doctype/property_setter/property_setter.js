// Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vmraid.ui.form.on('Property Setter', {
	validate: function(frm) {
		if(frm.doc.property_type=='Check' && !in_list(['0','1'], frm.doc.value)) {
			vmraid.throw(__('Value for a check field can be either 0 or 1'));
		}
	}
});
