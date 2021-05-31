# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

sitemap = 1

def get_context(context):
	context.doc = vmraid.get_doc("About Us Settings", "About Us Settings")

	return context
