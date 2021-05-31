# -*- coding: utf-8 -*-
# Copyright (c) 2018, VMRaid Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import vmraid, vmraid.utils, vmraid.utils.scheduler
from vmraid.desk.form import assign_to
import unittest

test_dependencies = ["User", "Notification"]

class TestNotification(unittest.TestCase):
	def setUp(self):
		vmraid.db.sql("""delete from `tabEmail Queue`""")
		vmraid.set_user("test@example.com")

		if not vmraid.db.exists('Notification', {'name': 'ToDo Status Update'}, 'name'):
			notification = vmraid.new_doc('Notification')
			notification.name = 'ToDo Status Update'
			notification.subject = 'ToDo Status Update'
			notification.document_type = 'ToDo'
			notification.event = 'Value Change'
			notification.value_changed = 'status'
			notification.send_to_all_assignees = 1
			notification.save()

		if not vmraid.db.exists('Notification', {'name': 'Contact Status Update'}, 'name'):
			notification = vmraid.new_doc('Notification')
			notification.name = 'Contact Status Update'
			notification.subject = 'Contact Status Update'
			notification.document_type = 'Contact'
			notification.event = 'Value Change'
			notification.value_changed = 'status'
			notification.message = 'Test Contact Update'
			notification.append('recipients', {
				'receiver_by_document_field': 'email_id,email_ids'
			})
			notification.save()


	def tearDown(self):
		vmraid.set_user("Administrator")

	def test_new_and_save(self):
		"""Check creating a new communication triggers a notification.
		"""
		communication = vmraid.new_doc("Communication")
		communication.communication_type = 'Comment'
		communication.subject = "test"
		communication.content = "test"
		communication.insert(ignore_permissions=True)

		self.assertTrue(vmraid.db.get_value("Email Queue", {"reference_doctype": "Communication",
			"reference_name": communication.name, "status":"Not Sent"}))
		vmraid.db.sql("""delete from `tabEmail Queue`""")

		communication.reload()
		communication.content = "test 2"
		communication.save()

		self.assertTrue(vmraid.db.get_value("Email Queue", {"reference_doctype": "Communication",
			"reference_name": communication.name, "status":"Not Sent"}))

		self.assertEqual(vmraid.db.get_value('Communication',
			communication.name, 'subject'), '__testing__')

	def test_condition(self):
		"""Check notification is triggered based on a condition.
		"""
		event = vmraid.new_doc("Event")
		event.subject = "test",
		event.event_type = "Private"
		event.starts_on  = "2014-06-06 12:00:00"
		event.insert()

		self.assertFalse(vmraid.db.get_value("Email Queue", {"reference_doctype": "Event",
			"reference_name": event.name, "status":"Not Sent"}))

		event.event_type = "Public"
		event.save()

		self.assertTrue(vmraid.db.get_value("Email Queue", {"reference_doctype": "Event",
			"reference_name": event.name, "status":"Not Sent"}))

		# Make sure that we track the triggered notifications in communication doctype.
		self.assertTrue(vmraid.db.get_value("Communication", {"reference_doctype": "Event",
			"reference_name": event.name, "communication_type": 'Automated Message'}))


	def test_invalid_condition(self):
		vmraid.set_user("Administrator")
		notification = vmraid.new_doc("Notification")
		notification.subject = "test"
		notification.document_type = "ToDo"
		notification.send_alert_on = "New"
		notification.message = "test"

		recipent = vmraid.new_doc("Notification Recipient")
		recipent.receiver_by_document_field = "owner"

		notification.recipents = recipent
		notification.condition = "test"

		self.assertRaises(vmraid.ValidationError, notification.save)
		notification.delete()


	def test_value_changed(self):
		event = vmraid.new_doc("Event")
		event.subject = "test",
		event.event_type = "Private"
		event.starts_on  = "2014-06-06 12:00:00"
		event.insert()

		self.assertFalse(vmraid.db.get_value("Email Queue", {"reference_doctype": "Event",
			"reference_name": event.name, "status":"Not Sent"}))

		event.subject = "test 1"
		event.save()

		self.assertFalse(vmraid.db.get_value("Email Queue", {"reference_doctype": "Event",
			"reference_name": event.name, "status":"Not Sent"}))

		event.description = "test"
		event.save()

		self.assertTrue(vmraid.db.get_value("Email Queue", {"reference_doctype": "Event",
			"reference_name": event.name, "status":"Not Sent"}))

	def test_alert_disabled_on_wrong_field(self):
		vmraid.set_user('Administrator')
		notification = vmraid.get_doc({
			"doctype": "Notification",
			"subject":"_Test Notification for wrong field",
			"document_type": "Event",
			"event": "Value Change",
			"attach_print": 0,
			"value_changed": "description1",
			"message": "Description changed",
			"recipients": [
				{ "receiver_by_document_field": "owner" }
			]
		}).insert()
		vmraid.db.commit()

		event = vmraid.new_doc("Event")
		event.subject = "test-2",
		event.event_type = "Private"
		event.starts_on  = "2014-06-06 12:00:00"
		event.insert()
		event.subject = "test 1"
		event.save()

		# verify that notification is disabled
		notification.reload()
		self.assertEqual(notification.enabled, 0)
		notification.delete()
		event.delete()

	def test_date_changed(self):

		event = vmraid.new_doc("Event")
		event.subject = "test",
		event.event_type = "Private"
		event.starts_on = "2014-01-01 12:00:00"
		event.insert()

		self.assertFalse(vmraid.db.get_value("Email Queue", {"reference_doctype": "Event",
			"reference_name": event.name, "status": "Not Sent"}))

		vmraid.set_user('Administrator')
		vmraid.get_doc('Scheduled Job Type', dict(method='vmraid.email.doctype.notification.notification.trigger_daily_alerts')).execute()

		# not today, so no alert
		self.assertFalse(vmraid.db.get_value("Email Queue", {"reference_doctype": "Event",
			"reference_name": event.name, "status": "Not Sent"}))

		event.starts_on  = vmraid.utils.add_days(vmraid.utils.nowdate(), 2) + " 12:00:00"
		event.save()

		# Value Change notification alert will be trigger as description is not changed
		# mail will not be sent
		self.assertFalse(vmraid.db.get_value("Email Queue", {"reference_doctype": "Event",
			"reference_name": event.name, "status": "Not Sent"}))

		vmraid.get_doc('Scheduled Job Type', dict(method='vmraid.email.doctype.notification.notification.trigger_daily_alerts')).execute()

		# today so show alert
		self.assertTrue(vmraid.db.get_value("Email Queue", {"reference_doctype": "Event",
			"reference_name": event.name, "status":"Not Sent"}))

	def test_cc_jinja(self):

		vmraid.db.sql("""delete from `tabUser` where email='test_jinja@example.com'""")
		vmraid.db.sql("""delete from `tabEmail Queue`""")
		vmraid.db.sql("""delete from `tabEmail Queue Recipient`""")

		test_user = vmraid.new_doc("User")
		test_user.name = 'test_jinja'
		test_user.first_name = 'test_jinja'
		test_user.email = 'test_jinja@example.com'

		test_user.insert(ignore_permissions=True)

		self.assertTrue(vmraid.db.get_value("Email Queue", {"reference_doctype": "User",
			"reference_name": test_user.name, "status":"Not Sent"}))

		self.assertTrue(vmraid.db.get_value("Email Queue Recipient", {"recipient": "test_jinja@example.com"}))

		vmraid.db.sql("""delete from `tabUser` where email='test_jinja@example.com'""")
		vmraid.db.sql("""delete from `tabEmail Queue`""")
		vmraid.db.sql("""delete from `tabEmail Queue Recipient`""")

	def test_notification_to_assignee(self):
		todo = vmraid.new_doc('ToDo')
		todo.description = 'Test Notification'
		todo.save()

		assign_to.add({
			"assign_to": ["test2@example.com"],
			"doctype": todo.doctype,
			"name": todo.name,
			"description": "Close this Todo"
		})

		assign_to.add({
			"assign_to": ["test1@example.com"],
			"doctype": todo.doctype,
			"name": todo.name,
			"description": "Close this Todo"
		})

		#change status of todo
		todo.status = 'Closed'
		todo.save()

		email_queue = vmraid.get_doc('Email Queue', {'reference_doctype': 'ToDo',
			'reference_name': todo.name})

		self.assertTrue(email_queue)

		recipients = [d.recipient for d in email_queue.recipients]
		self.assertTrue('test2@example.com' in recipients)
		self.assertTrue('test1@example.com' in recipients)

	def test_notification_by_child_table_field(self):
		contact = vmraid.new_doc('Contact')
		contact.first_name = 'John Doe'
		contact.status = 'Open'
		contact.append('email_ids', {
			'email_id': 'test2@example.com',
			'is_primary': 1
		})

		contact.append('email_ids', {
			'email_id': 'test1@example.com'
		})

		contact.save()

		#change status of contact
		contact.status = 'Replied'
		contact.save()

		email_queue = vmraid.get_doc('Email Queue', {'reference_doctype': 'Contact',
			'reference_name': contact.name})

		self.assertTrue(email_queue)

		recipients = [d.recipient for d in email_queue.recipients]
		self.assertTrue('test2@example.com' in recipients)
		self.assertTrue('test1@example.com' in recipients)


