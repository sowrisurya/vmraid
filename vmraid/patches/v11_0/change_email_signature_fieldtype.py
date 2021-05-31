# Copyright (c) 2018, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	signatures = vmraid.db.get_list('User', {'email_signature': ['!=', '']},['name', 'email_signature'])
	vmraid.reload_doc('core', 'doctype', 'user')
	for d in signatures:
		signature = d.get('email_signature')
		signature = signature.replace('\n', '<br>')
		signature = '<div>' + signature + '</div>'
		vmraid.db.set_value('User', d.get('name'), 'email_signature', signature)