# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	try:
		vmraid.db.sql("alter table `tabEmail Queue` change `ref_docname` `reference_name` varchar(255)")
	except Exception as e:
		if not vmraid.db.is_table_or_column_missing(e):
			raise

	try:
		vmraid.db.sql("alter table `tabEmail Queue` change `ref_doctype` `reference_doctype` varchar(255)")
	except Exception as e:
		if not vmraid.db.is_table_or_column_missing(e):
			raise
	vmraid.reload_doctype("Email Queue")
