from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.db.sql("""delete from `tabCustom DocPerm`
		where parent not in ( select name from `tabDocType` )
	""")
