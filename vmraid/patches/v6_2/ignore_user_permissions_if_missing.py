from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doctype("System Settings")
	system_settings = vmraid.get_doc("System Settings")
	system_settings.flags.ignore_mandatory = 1
	system_settings.save()
