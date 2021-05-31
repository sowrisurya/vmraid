# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import vmraid

def add_custom_field(doctype, fieldname, fieldtype='Data', options=None):
	vmraid.get_doc({
		"doctype": "Custom Field",
		"dt": doctype,
		"fieldname": fieldname,
		"fieldtype": fieldtype,
		"options": options
	}).insert()

def clear_custom_fields(doctype):
	vmraid.db.sql('delete from `tabCustom Field` where dt=%s', doctype)
	vmraid.clear_cache(doctype=doctype)
