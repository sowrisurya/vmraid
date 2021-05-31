# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	for doctype in vmraid.db.sql_list("""select name from `tabDocType` where istable=1"""):
		vmraid.db.sql("""delete from `tab{0}` where parent like "old_par%:%" """.format(doctype))
	vmraid.db.sql("""delete from `tabDocField` where parent="0" """)
