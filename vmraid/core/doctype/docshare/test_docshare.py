# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# See license.txt

from __future__ import unicode_literals
import vmraid
import vmraid.share
import unittest
from vmraid.automation.doctype.auto_repeat.test_auto_repeat import create_submittable_doctype

test_dependencies = ['User']

class TestDocShare(unittest.TestCase):
	def setUp(self):
		self.user = "test@example.com"
		self.event = vmraid.get_doc({"doctype": "Event",
			"subject": "test share event",
			"starts_on": "2015-01-01 10:00:00",
			"event_type": "Private"}).insert()

	def tearDown(self):
		vmraid.set_user("Administrator")
		self.event.delete()

	def test_add(self):
		# user not shared
		self.assertTrue(self.event.name not in vmraid.share.get_shared("Event", self.user))
		vmraid.share.add("Event", self.event.name, self.user)
		self.assertTrue(self.event.name in vmraid.share.get_shared("Event", self.user))

	def test_doc_permission(self):
		vmraid.set_user(self.user)
		self.assertFalse(self.event.has_permission())

		vmraid.set_user("Administrator")
		vmraid.share.add("Event", self.event.name, self.user)

		vmraid.set_user(self.user)
		self.assertTrue(self.event.has_permission())

	def test_share_permission(self):
		vmraid.share.add("Event", self.event.name, self.user, write=1, share=1)

		vmraid.set_user(self.user)
		self.assertTrue(self.event.has_permission("share"))

		# test cascade
		self.assertTrue(self.event.has_permission("read"))
		self.assertTrue(self.event.has_permission("write"))

	def test_set_permission(self):
		vmraid.share.add("Event", self.event.name, self.user)

		vmraid.set_user(self.user)
		self.assertFalse(self.event.has_permission("share"))

		vmraid.set_user("Administrator")
		vmraid.share.set_permission("Event", self.event.name, self.user, "share")

		vmraid.set_user(self.user)
		self.assertTrue(self.event.has_permission("share"))

	def test_permission_to_share(self):
		vmraid.set_user(self.user)
		self.assertRaises(vmraid.PermissionError, vmraid.share.add, "Event", self.event.name, self.user)

		vmraid.set_user("Administrator")
		vmraid.share.add("Event", self.event.name, self.user, write=1, share=1)

		# test not raises
		vmraid.set_user(self.user)
		vmraid.share.add("Event", self.event.name, "test1@example.com", write=1, share=1)

	def test_remove_share(self):
		vmraid.share.add("Event", self.event.name, self.user, write=1, share=1)

		vmraid.set_user(self.user)
		self.assertTrue(self.event.has_permission("share"))

		vmraid.set_user("Administrator")
		vmraid.share.remove("Event", self.event.name, self.user)

		vmraid.set_user(self.user)
		self.assertFalse(self.event.has_permission("share"))

	def test_share_with_everyone(self):
		self.assertTrue(self.event.name not in vmraid.share.get_shared("Event", self.user))

		vmraid.share.set_permission("Event", self.event.name, None, "read", everyone=1)
		self.assertTrue(self.event.name in vmraid.share.get_shared("Event", self.user))
		self.assertTrue(self.event.name in vmraid.share.get_shared("Event", "test1@example.com"))
		self.assertTrue(self.event.name not in vmraid.share.get_shared("Event", "Guest"))

		vmraid.share.set_permission("Event", self.event.name, None, "read", value=0, everyone=1)
		self.assertTrue(self.event.name not in vmraid.share.get_shared("Event", self.user))
		self.assertTrue(self.event.name not in vmraid.share.get_shared("Event", "test1@example.com"))
		self.assertTrue(self.event.name not in vmraid.share.get_shared("Event", "Guest"))

	def test_share_with_submit_perm(self):
		doctype = "Test DocShare with Submit"
		create_submittable_doctype(doctype, submit_perms=0)

		submittable_doc = vmraid.get_doc(dict(doctype=doctype, test="test docshare with submit")).insert()

		vmraid.set_user(self.user)
		self.assertFalse(vmraid.has_permission(doctype, "submit", user=self.user))

		vmraid.set_user("Administrator")
		vmraid.share.add(doctype, submittable_doc.name, self.user, submit=1)

		vmraid.set_user(self.user)
		self.assertTrue(vmraid.has_permission(doctype, "submit", doc=submittable_doc.name, user=self.user))

		# test cascade
		self.assertTrue(vmraid.has_permission(doctype, "read", doc=submittable_doc.name, user=self.user))
		self.assertTrue(vmraid.has_permission(doctype, "write", doc=submittable_doc.name, user=self.user))

		vmraid.share.remove(doctype, submittable_doc.name, self.user)
