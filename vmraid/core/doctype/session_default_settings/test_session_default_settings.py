# -*- coding: utf-8 -*-
# Copyright (c) 2019, VMRaid Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import vmraid
import unittest
from vmraid.core.doctype.session_default_settings.session_default_settings import set_session_default_values, clear_session_defaults

class TestSessionDefaultSettings(unittest.TestCase):
	def test_set_session_default_settings(self):
		vmraid.set_user("Administrator")
		settings = vmraid.get_single("Session Default Settings")
		settings.session_defaults = []
		settings.append("session_defaults", {
			"ref_doctype": "Role"
		})
		settings.save()

		set_session_default_values({"role": "Website Manager"})

		todo = vmraid.get_doc(dict(doctype="ToDo", description="test session defaults set", assigned_by="Administrator")).insert()
		self.assertEqual(todo.role, "Website Manager")

	def test_clear_session_defaults(self):
		clear_session_defaults()
		todo = vmraid.get_doc(dict(doctype="ToDo", description="test session defaults cleared", assigned_by="Administrator")).insert()
		self.assertNotEqual(todo.role, "Website Manager")
