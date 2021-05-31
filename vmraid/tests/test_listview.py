# Copyright (c) 2019, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import unittest
import vmraid
import json

from vmraid.desk.listview import get_list_settings, set_list_settings, get_group_by_count

class TestListView(unittest.TestCase):
	def setUp(self):
		if vmraid.db.exists("List View Settings", "DocType"):
			vmraid.delete_doc("List View Settings", "DocType")

	def test_get_list_settings_without_settings(self):
		self.assertIsNone(get_list_settings("DocType"), None)

	def test_get_list_settings_with_default_settings(self):
		vmraid.get_doc({"doctype": "List View Settings", "name": "DocType"}).insert()
		settings = get_list_settings("DocType")
		self.assertIsNotNone(settings)

		self.assertEqual(settings.disable_auto_refresh, 0)
		self.assertEqual(settings.disable_count, 0)
		self.assertEqual(settings.disable_sidebar_stats, 0)

	def test_get_list_settings_with_non_default_settings(self):
		vmraid.get_doc({"doctype": "List View Settings", "name": "DocType", "disable_count": 1}).insert()
		settings = get_list_settings("DocType")
		self.assertIsNotNone(settings)

		self.assertEqual(settings.disable_auto_refresh, 0)
		self.assertEqual(settings.disable_count, 1)
		self.assertEqual(settings.disable_sidebar_stats, 0)

	def test_set_list_settings_without_settings(self):
		set_list_settings("DocType", json.dumps({}))
		settings = vmraid.get_doc("List View Settings","DocType")

		self.assertEqual(settings.disable_auto_refresh, 0)
		self.assertEqual(settings.disable_count, 0)
		self.assertEqual(settings.disable_sidebar_stats, 0)

	def test_set_list_settings_with_existing_settings(self):
		vmraid.get_doc({"doctype": "List View Settings", "name": "DocType", "disable_count": 1}).insert()
		set_list_settings("DocType", json.dumps({"disable_count": 0, "disable_auto_refresh": 1}))
		settings = vmraid.get_doc("List View Settings","DocType")

		self.assertEqual(settings.disable_auto_refresh, 1)
		self.assertEqual(settings.disable_count, 0)
		self.assertEqual(settings.disable_sidebar_stats, 0)

	def test_list_view_child_table_filter_with_created_by_filter(self):
		if vmraid.db.exists("Note", "Test created by filter with child table filter"):
			vmraid.delete_doc("Note", "Test created by filter with child table filter")

		doc = vmraid.get_doc({"doctype": "Note", "title": "Test created by filter with child table filter", "public": 1})
		doc.append("seen_by", {"user": "Administrator"})
		doc.insert()

		data = {d.name: d.count for d in get_group_by_count('Note', '[["Note Seen By","user","=","Administrator"]]', 'owner')}
		self.assertEqual(data['Administrator'], 1)