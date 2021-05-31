# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	for d in vmraid.get_all("Property Setter", fields=["name", "doc_type"],
		filters={"doctype_or_field": "DocField", "property": "allow_on_submit", "value": "1"}):
		vmraid.delete_doc("Property Setter", d.name)
		vmraid.clear_cache(doctype=d.doc_type)
