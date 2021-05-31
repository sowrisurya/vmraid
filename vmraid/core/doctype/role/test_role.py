# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import vmraid
import unittest

test_records = vmraid.get_test_records('Role')

class TestUser(unittest.TestCase):
	def test_disable_role(self):
		vmraid.get_doc("User", "test@example.com").add_roles("_Test Role 3")

		role = vmraid.get_doc("Role", "_Test Role 3")
		role.disabled = 1
		role.save()

		self.assertTrue("_Test Role 3" not in vmraid.get_roles("test@example.com"))

		role = vmraid.get_doc("Role", "_Test Role 3")
		role.disabled = 0
		role.save()

		vmraid.get_doc("User", "test@example.com").add_roles("_Test Role 3")
		self.assertTrue("_Test Role 3" in vmraid.get_roles("test@example.com"))

	def test_change_desk_access(self):
		'''if we change desk acecss from role, remove from user'''
		vmraid.delete_doc_if_exists('User', 'test-user-for-desk-access@example.com')
		vmraid.delete_doc_if_exists('Role', 'desk-access-test')
		user = vmraid.get_doc(dict(
			doctype='User',
			email='test-user-for-desk-access@example.com',
			first_name='test')).insert()
		role = vmraid.get_doc(dict(
			doctype = 'Role',
			role_name = 'desk-access-test',
			desk_access = 0
		)).insert()
		user.add_roles(role.name)
		user.save()
		self.assertTrue(user.user_type=='Website User')
		role.desk_access = 1
		role.save()
		user.reload()
		self.assertTrue(user.user_type=='System User')
		role.desk_access = 0
		role.save()
		user.reload()
		self.assertTrue(user.user_type=='Website User')
