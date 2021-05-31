# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid
import vmraid.permissions

def execute():
	vmraid.reload_doc("core", "doctype", "docperm")
	table_columns = vmraid.db.get_table_columns("DocPerm")

	if "restricted" in table_columns:
		vmraid.db.sql("""update `tabDocPerm` set apply_user_permissions=1 where apply_user_permissions=0
			and restricted=1""")

	if "match" in table_columns:
		vmraid.db.sql("""update `tabDocPerm` set apply_user_permissions=1
			where apply_user_permissions=0 and ifnull(`match`, '')!=''""")

	# change Restriction to User Permission in tabDefaultValue
	vmraid.db.sql("""update `tabDefaultValue` set parenttype='User Permission' where parenttype='Restriction'""")

	vmraid.clear_cache()

