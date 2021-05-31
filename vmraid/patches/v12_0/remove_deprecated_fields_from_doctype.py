import vmraid

def execute():
	vmraid.reload_doc('core', 'doctype', 'doctype_link')
	vmraid.reload_doc('core', 'doctype', 'doctype_action')
	vmraid.reload_doc('core', 'doctype', 'doctype')
	vmraid.model.delete_fields({
		'DocType': ['hide_heading', 'image_view', 'read_only_onload']
	}, delete=1)

	vmraid.db.sql('''
		DELETE from `tabProperty Setter`
		WHERE property = 'read_only_onload'
	''')
