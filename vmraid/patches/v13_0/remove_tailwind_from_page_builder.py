# Copyright (c) 2020, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid


def execute():
	vmraid.reload_doc("website", "doctype", "web_page_block")
	# remove unused templates
	vmraid.delete_doc("Web Template", "Navbar with Links on Right", force=1)
	vmraid.delete_doc("Web Template", "Footer Horizontal", force=1)

