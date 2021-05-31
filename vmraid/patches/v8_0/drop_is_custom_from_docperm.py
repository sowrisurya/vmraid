from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doctype('DocPerm')
	if vmraid.db.has_column('DocPerm', 'is_custom'):
		vmraid.db.commit()
		vmraid.db.sql('alter table `tabDocPerm` drop column is_custom')