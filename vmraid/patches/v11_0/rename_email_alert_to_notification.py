from __future__ import unicode_literals
import vmraid
from vmraid.model.rename_doc import rename_doc

def execute():
	if vmraid.db.table_exists("Email Alert Recipient") and not vmraid.db.table_exists("Notification Recipient"):
		rename_doc('DocType', 'Email Alert Recipient', 'Notification Recipient')
		vmraid.reload_doc('email', 'doctype', 'notification_recipient')

	if vmraid.db.table_exists("Email Alert") and not vmraid.db.table_exists("Notification"):
		rename_doc('DocType', 'Email Alert', 'Notification')
		vmraid.reload_doc('email', 'doctype', 'notification')
