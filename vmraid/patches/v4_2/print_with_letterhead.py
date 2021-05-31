# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc("core", "doctype", "print_settings")
	print_settings = vmraid.get_doc("Print Settings")
	print_settings.with_letterhead = 1
	print_settings.save()
