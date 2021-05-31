# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	user_owner = vmraid.db.get_value("Custom Field", {"fieldname": "user_owner"})
	if user_owner:
		vmraid.delete_doc("Custom Field", user_owner)
