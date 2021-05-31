from __future__ import unicode_literals
import vmraid

def execute():
	if vmraid.db.has_column('DocField', 'in_filter'):
		vmraid.db.sql('alter table tabDocField drop column in_filter')
	vmraid.clear_cache(doctype="DocField")