from __future__ import unicode_literals
import vmraid

def execute():
	if vmraid.db.has_column('DocType', 'in_dialog'):
		vmraid.db.sql('alter table tabDocType drop column in_dialog')
	vmraid.clear_cache(doctype="DocType")