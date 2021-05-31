# Copyright (c) 2020, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	"""Enable all the existing Client script"""

	vmraid.db.sql("""
		UPDATE `tabClient Script` SET enabled=1
	""")