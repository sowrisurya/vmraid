# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc("email", "doctype", "email_group_member")
	if "newsletter_list" in vmraid.db.get_table_columns("Email Group Member"):
		vmraid.db.sql("""update `tabEmail Group Member` set email_group = newsletter_list 
			where email_group is null or email_group = ''""")