# Copyright (c) 2020, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	"""Set default module for standard Web Template, if none."""
	vmraid.reload_doc('website', 'doctype', 'Web Template Field')
	vmraid.reload_doc('website', 'doctype', 'web_template')

	standard_templates = vmraid.get_list('Web Template', {'standard': 1})
	for template in standard_templates:
		doc = vmraid.get_doc('Web Template', template.name)
		if not doc.module:
			doc.module = 'Website'
			doc.save()
