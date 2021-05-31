# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc("core", "doctype", "sms_parameter")
	sms_sender_name = vmraid.db.get_single_value("SMS Settings", "sms_sender_name")
	if sms_sender_name:
		vmraid.reload_doc("core", "doctype", "sms_settings")
		sms_settings = vmraid.get_doc("SMS Settings")
		sms_settings.append("parameters", {
			"parameter": "sender_name",
			"value": sms_sender_name
		})
		sms_settings.flags.ignore_mandatory = True
		sms_settings.flags.ignore_permissions = True
		sms_settings.save()
