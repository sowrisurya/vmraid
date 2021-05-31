from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc("email", "doctype", "email_account")
	if vmraid.db.has_column('Email Account', 'pop3_server'):
		vmraid.db.sql("update `tabEmail Account` set email_server = pop3_server")
