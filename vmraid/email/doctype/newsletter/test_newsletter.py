# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals

import unittest
from random import choice

import vmraid
from vmraid.email.doctype.newsletter.newsletter import (
	confirmed_unsubscribe,
	send_scheduled_email,
)
from vmraid.email.doctype.newsletter.newsletter import get_newsletter_list
from vmraid.email.queue import flush
from vmraid.utils import add_days, getdate

test_dependencies = ["Email Group"]
emails = [
	"test_subscriber1@example.com",
	"test_subscriber2@example.com",
	"test_subscriber3@example.com",
	"test1@example.com",
]


class TestNewsletter(unittest.TestCase):
	def setUp(self):
		vmraid.set_user("Administrator")
		vmraid.db.sql("delete from `tabEmail Group Member`")

		if not vmraid.db.exists("Email Group", "_Test Email Group"):
			vmraid.get_doc({"doctype": "Email Group", "title": "_Test Email Group"}).insert()

		for email in emails:
			vmraid.get_doc({
				"doctype": "Email Group Member",
				"email": email,
				"email_group": "_Test Email Group"
			}).insert()

	def test_send(self):
		self.send_newsletter()

		email_queue_list = [vmraid.get_doc("Email Queue", e.name) for e in vmraid.get_all("Email Queue")]
		self.assertEqual(len(email_queue_list), 4)

		recipients = set([e.recipients[0].recipient for e in email_queue_list])
		self.assertTrue(set(emails).issubset(recipients))

	def test_unsubscribe(self):
		name = self.send_newsletter()
		to_unsubscribe = choice(emails)
		group = vmraid.get_all("Newsletter Email Group", filters={"parent": name}, fields=["email_group"])

		flush(from_test=True)
		confirmed_unsubscribe(to_unsubscribe, group[0].email_group)

		name = self.send_newsletter()
		email_queue_list = [
			vmraid.get_doc("Email Queue", e.name) for e in vmraid.get_all("Email Queue")
		]
		self.assertEqual(len(email_queue_list), 3)
		recipients = [e.recipients[0].recipient for e in email_queue_list]

		for email in emails:
			if email != to_unsubscribe:
				self.assertTrue(email in recipients)

	@staticmethod
	def send_newsletter(published=0, schedule_send=None):
		vmraid.db.sql("delete from `tabEmail Queue`")
		vmraid.db.sql("delete from `tabEmail Queue Recipient`")
		vmraid.db.sql("delete from `tabNewsletter`")
		newsletter = vmraid.get_doc({
			"doctype": "Newsletter",
			"subject": "_Test Newsletter",
			"send_from": "Test Sender <test_sender@example.com>",
			"content_type": "Rich Text",
			"message": "Testing my news.",
			"published": published,
			"schedule_sending": bool(schedule_send),
			"schedule_send": schedule_send
		}).insert(ignore_permissions=True)

		newsletter.append("email_group", {"email_group": "_Test Email Group"})
		newsletter.save()
		if schedule_send:
			send_scheduled_email()
			return

		newsletter.send_emails()
		return newsletter.name

	def test_portal(self):
		self.send_newsletter(1)
		vmraid.set_user("test1@example.com")
		newsletters = get_newsletter_list("Newsletter", None, None, 0)
		self.assertEqual(len(newsletters), 1)

	def test_newsletter_context(self):
		context = vmraid._dict()
		newsletter_name = self.send_newsletter(1)
		vmraid.set_user("test2@example.com")
		doc = vmraid.get_doc("Newsletter", newsletter_name)
		doc.get_context(context)
		self.assertEqual(context.no_cache, 1)
		self.assertTrue("attachments" not in list(context))

	def test_schedule_send(self):
		self.send_newsletter(schedule_send=add_days(getdate(), -1))

		email_queue_list = [vmraid.get_doc('Email Queue', e.name) for e in vmraid.get_all("Email Queue")]
		self.assertEqual(len(email_queue_list), 4)
		recipients = [e.recipients[0].recipient for e in email_queue_list]
		for email in emails:
			self.assertTrue(email in recipients)
