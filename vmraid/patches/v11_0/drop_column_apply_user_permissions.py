from __future__ import unicode_literals
import vmraid

def execute():
	column = 'apply_user_permissions'
	to_remove = ['DocPerm', 'Custom DocPerm']

	for doctype in to_remove:
		if vmraid.db.table_exists(doctype):
			if column in vmraid.db.get_table_columns(doctype):
				vmraid.db.sql("alter table `tab{0}` drop column {1}".format(doctype, column))

	vmraid.reload_doc('core', 'doctype', 'docperm', force=True)
	vmraid.reload_doc('core', 'doctype', 'custom_docperm', force=True)

