# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# See license.txt

from __future__ import unicode_literals
import vmraid, os
import unittest, email

from vmraid.test_runner import make_test_records

make_test_records("User")
make_test_records("Email Account")

from vmraid.core.doctype.communication.email import make
from vmraid.desk.form.load import get_attachments
from vmraid.email.doctype.email_account.email_account import notify_unreplied
from datetime import datetime, timedelta

class TestEmailAccount(unittest.TestCase):
	def setUp(self):
		vmraid.flags.mute_emails = False
		vmraid.flags.sent_mail = None

		email_account = vmraid.get_doc("Email Account", "_Test Email Account 1")
		email_account.db_set("enable_incoming", 1)
		vmraid.db.sql('delete from `tabEmail Queue`')

	def tearDown(self):
		email_account = vmraid.get_doc("Email Account", "_Test Email Account 1")
		email_account.db_set("enable_incoming", 0)

	def test_incoming(self):
		cleanup("test_sender@example.com")

		with open(os.path.join(os.path.dirname(__file__), "test_mails", "incoming-1.raw"), "r") as f:
			test_mails = [f.read()]

		email_account = vmraid.get_doc("Email Account", "_Test Email Account 1")
		email_account.receive(test_mails=test_mails)

		comm = vmraid.get_doc("Communication", {"sender": "test_sender@example.com"})
		self.assertTrue("test_receiver@example.com" in comm.recipients)

		# check if todo is created
		self.assertTrue(vmraid.db.get_value(comm.reference_doctype, comm.reference_name, "name"))

	def test_unread_notification(self):
		self.test_incoming()

		comm = vmraid.get_doc("Communication", {"sender": "test_sender@example.com"})
		comm.db_set("creation", datetime.now() - timedelta(seconds = 30 * 60))

		vmraid.db.sql("DELETE FROM `tabEmail Queue`")
		notify_unreplied()
		self.assertTrue(vmraid.db.get_value("Email Queue", {"reference_doctype": comm.reference_doctype,
			"reference_name": comm.reference_name, "status":"Not Sent"}))

	def test_incoming_with_attach(self):
		cleanup("test_sender@example.com")

		existing_file = vmraid.get_doc({'doctype': 'File', 'file_name': 'erpadda-conf-14.png'})
		vmraid.delete_doc("File", existing_file.name)

		with open(os.path.join(os.path.dirname(__file__), "test_mails", "incoming-2.raw"), "r") as testfile:
			test_mails = [testfile.read()]

		email_account = vmraid.get_doc("Email Account", "_Test Email Account 1")
		email_account.receive(test_mails=test_mails)

		comm = vmraid.get_doc("Communication", {"sender": "test_sender@example.com"})
		self.assertTrue("test_receiver@example.com" in comm.recipients)

		# check attachment
		attachments = get_attachments(comm.doctype, comm.name)
		self.assertTrue("erpadda-conf-14.png" in [f.file_name for f in attachments])

		# cleanup
		existing_file = vmraid.get_doc({'doctype': 'File', 'file_name': 'erpadda-conf-14.png'})
		vmraid.delete_doc("File", existing_file.name)


	def test_incoming_attached_email_from_outlook_plain_text_only(self):
		cleanup("test_sender@example.com")

		with open(os.path.join(os.path.dirname(__file__), "test_mails", "incoming-3.raw"), "r") as f:
			test_mails = [f.read()]

		email_account = vmraid.get_doc("Email Account", "_Test Email Account 1")
		email_account.receive(test_mails=test_mails)

		comm = vmraid.get_doc("Communication", {"sender": "test_sender@example.com"})
		self.assertTrue("From: \"Microsoft Outlook\" &lt;test_sender@example.com&gt;" in comm.content)
		self.assertTrue("This is an e-mail message sent automatically by Microsoft Outlook while" in comm.content)

	def test_incoming_attached_email_from_outlook_layers(self):
		cleanup("test_sender@example.com")

		with open(os.path.join(os.path.dirname(__file__), "test_mails", "incoming-4.raw"), "r") as f:
			test_mails = [f.read()]

		email_account = vmraid.get_doc("Email Account", "_Test Email Account 1")
		email_account.receive(test_mails=test_mails)

		comm = vmraid.get_doc("Communication", {"sender": "test_sender@example.com"})
		self.assertTrue("From: \"Microsoft Outlook\" &lt;test_sender@example.com&gt;" in comm.content)
		self.assertTrue("This is an e-mail message sent automatically by Microsoft Outlook while" in comm.content)

	def test_outgoing(self):
		make(subject = "test-mail-000", content="test mail 000", recipients="test_receiver@example.com",
			send_email=True, sender="test_sender@example.com")

		mail = email.message_from_string(vmraid.get_last_doc("Email Queue").message)
		self.assertTrue("test-mail-000" in mail.get("Subject"))

	def test_sendmail(self):
		vmraid.sendmail(sender="test_sender@example.com", recipients="test_recipient@example.com",
			content="test mail 001", subject="test-mail-001", delayed=False)

		sent_mail = email.message_from_string(vmraid.safe_decode(vmraid.flags.sent_mail))
		self.assertTrue("test-mail-001" in sent_mail.get("Subject"))

	def test_print_format(self):
		make(sender="test_sender@example.com", recipients="test_recipient@example.com",
			content="test mail 001", subject="test-mail-002", doctype="Email Account",
			name="_Test Email Account 1", print_format="Standard", send_email=True)

		sent_mail = email.message_from_string(vmraid.get_last_doc("Email Queue").message)
		self.assertTrue("test-mail-002" in sent_mail.get("Subject"))

	def test_threading(self):
		cleanup(["in", ['test_sender@example.com', 'test@example.com']])

		# send
		sent_name = make(subject = "Test", content="test content",
			recipients="test_receiver@example.com", sender="test@example.com",doctype="ToDo",name=vmraid.get_last_doc("ToDo").name,
			send_email=True)["name"]

		sent_mail = email.message_from_string(vmraid.get_last_doc("Email Queue").message)

		with open(os.path.join(os.path.dirname(__file__), "test_mails", "reply-1.raw"), "r") as f:
			raw = f.read()
			raw = raw.replace("<-- in-reply-to -->", sent_mail.get("Message-Id"))
			test_mails = [raw]

		# parse reply
		email_account = vmraid.get_doc("Email Account", "_Test Email Account 1")
		email_account.receive(test_mails=test_mails)

		sent = vmraid.get_doc("Communication", sent_name)

		comm = vmraid.get_doc("Communication", {"sender": "test_sender@example.com"})
		self.assertEqual(comm.reference_doctype, sent.reference_doctype)
		self.assertEqual(comm.reference_name, sent.reference_name)

	def test_threading_by_subject(self):
		cleanup(["in", ['test_sender@example.com', 'test@example.com']])

		with open(os.path.join(os.path.dirname(__file__), "test_mails", "reply-2.raw"), "r") as f:
			test_mails = [f.read()]

		with open(os.path.join(os.path.dirname(__file__), "test_mails", "reply-3.raw"), "r") as f:
			test_mails.append(f.read())

		# parse reply
		email_account = vmraid.get_doc("Email Account", "_Test Email Account 1")
		email_account.receive(test_mails=test_mails)

		comm_list = vmraid.get_all("Communication", filters={"sender":"test_sender@example.com"},
			fields=["name", "reference_doctype", "reference_name"])

		# both communications attached to the same reference
		self.assertEqual(comm_list[0].reference_doctype, comm_list[1].reference_doctype)
		self.assertEqual(comm_list[0].reference_name, comm_list[1].reference_name)

	def test_threading_by_message_id(self):
		cleanup()
		vmraid.db.sql("""delete from `tabEmail Queue`""")

		# reference document for testing
		event = vmraid.get_doc(dict(doctype='Event', subject='test-message')).insert()

		# send a mail against this
		vmraid.sendmail(recipients='test@example.com', subject='test message for threading',
			message='testing', reference_doctype=event.doctype, reference_name=event.name)

		last_mail = vmraid.get_doc('Email Queue', dict(reference_name=event.name))

		# get test mail with message-id as in-reply-to
		with open(os.path.join(os.path.dirname(__file__), "test_mails", "reply-4.raw"), "r") as f:
			test_mails = [f.read().replace('{{ message_id }}', last_mail.message_id)]

		# pull the mail
		email_account = vmraid.get_doc("Email Account", "_Test Email Account 1")
		email_account.receive(test_mails=test_mails)

		comm_list = vmraid.get_all("Communication", filters={"sender":"test_sender@example.com"},
			fields=["name", "reference_doctype", "reference_name"])

		# check if threaded correctly
		self.assertEqual(comm_list[0].reference_doctype, event.doctype)
		self.assertEqual(comm_list[0].reference_name, event.name)

def cleanup(sender=None):
	filters = {}
	if sender:
		filters.update({"sender": sender})

	names = vmraid.get_list("Communication", filters=filters, fields=["name"])
	for name in names:
		vmraid.delete_doc_if_exists("Communication", name.name)
		vmraid.delete_doc_if_exists("Communication Link", {"parent": name.name})