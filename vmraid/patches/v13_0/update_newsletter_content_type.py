# Copyright (c) 2020, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc('email', 'doctype', 'Newsletter')
	vmraid.db.sql("""
		UPDATE tabNewsletter
		SET content_type = 'Rich Text'
	""")
