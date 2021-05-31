from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc('email', 'doctype', 'email_queue_recipient')
	vmraid.db.sql('update `tabEmail Queue Recipient` set parenttype="recipients"')