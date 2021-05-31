from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doctype('System Settings')
	doc = vmraid.get_single('System Settings')
	doc.enable_chat = 1

	# Changes prescribed by Nabin Hait (nabin@vmraid.io)
	doc.flags.ignore_mandatory   = True
	doc.flags.ignore_permissions = True

	doc.save()