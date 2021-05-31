# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc("core", "doctype", "outgoing_email_settings")
	if (vmraid.db.get_value("Outgoing Email Settings", "Outgoing Email Settings", "mail_server") or "").strip():
		vmraid.db.set_value("Outgoing Email Settings", "Outgoing Email Settings", "enabled", 1)
