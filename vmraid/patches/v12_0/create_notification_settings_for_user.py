from __future__ import unicode_literals
import vmraid
from vmraid.desk.doctype.notification_settings.notification_settings import create_notification_settings

def execute():
	vmraid.reload_doc('desk', 'doctype', 'notification_settings')
	vmraid.reload_doc('desk', 'doctype', 'notification_subscribed_document')

	users = vmraid.db.get_all('User', fields=['name'])
	for user in users:
		create_notification_settings(user.name)