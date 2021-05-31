// Copyright (c) 2019, VMRaid Technologies and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Document Type Mapping', {
	local_doctype: function(frm) {
		if (frm.doc.local_doctype) {
			vmraid.model.clear_table(frm.doc, 'field_mapping');
			let fields = frm.events.get_fields(frm);
			$.each(fields, function(i, data) {
				let row = vmraid.model.add_child(frm.doc, 'Document Type Mapping', 'field_mapping');
				row.local_fieldname = data;
			});
			refresh_field('field_mapping');
		}
	},

	get_fields: function(frm) {
		let filtered_fields = [];
		vmraid.model.with_doctype(frm.doc.local_doctype, ()=> {
			vmraid.get_meta(frm.doc.local_doctype).fields.map( field => {
				if (field.fieldname !== 'remote_docname' && field.fieldname !== 'remote_site_name' && vmraid.model.is_value_type(field) && !field.hidden) {
					filtered_fields.push(field.fieldname);
				}
			});
		});
		return filtered_fields;
	}
});
