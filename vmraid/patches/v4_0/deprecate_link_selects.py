# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	for name in vmraid.db.sql_list("""select name from `tabCustom Field`
		where fieldtype="Select" and options like "link:%" """):
		custom_field = vmraid.get_doc("Custom Field", name)
		custom_field.fieldtype = "Link"
		custom_field.options = custom_field.options[5:]
		custom_field.save()
