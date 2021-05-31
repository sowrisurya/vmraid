import os
import unittest

import vmraid
from vmraid.utils import add_to_date, now
from vmraid.exceptions import DoesNotExistError

from random import choice, sample
from vmraid.model.base_document import get_controller
from vmraid.modules.utils import get_doc_path


class TestRenameDoc(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		"""Setting Up data for the tests defined under TestRenameDoc"""
		# set developer_mode to rename doc controllers
		self._original_developer_flag = vmraid.conf.developer_mode
		vmraid.conf.developer_mode = 1

		# data generation: for base and merge tests
		self.available_documents = []
		self.test_doctype = "ToDo"

		for num in range(1, 5):
			doc = vmraid.get_doc({
				"doctype": self.test_doctype,
				"date": add_to_date(now(), days=num),
				"description": "this is todo #{}".format(num),
			}).insert()
			self.available_documents.append(doc.name)

		#  data generation: for controllers tests
		self.doctype = vmraid._dict({
			"old": "Test Rename Document Old",
			"new": "Test Rename Document New",
		})

		vmraid.get_doc({
			"doctype": "DocType",
			"module": "Custom",
			"name": self.doctype.old,
			"custom": 0,
			"fields": [
				{"label": "Some Field", "fieldname": "some_fieldname", "fieldtype": "Data"}
			],
			"permissions": [{"role": "System Manager", "read": 1}],
		}).insert()

	@classmethod
	def tearDownClass(self):
		"""Deleting data generated for the tests defined under TestRenameDoc"""
		# delete the documents created
		for docname in self.available_documents:
			vmraid.delete_doc(self.test_doctype, docname)

		for dt in self.doctype.values():
			if vmraid.db.exists("DocType", dt):
				vmraid.delete_doc("DocType", dt)
				vmraid.db.sql_ddl(f"DROP TABLE IF EXISTS `tab{dt}`")

		vmraid.delete_doc_if_exists("Renamed Doc", "ToDo")

		# reset original value of developer_mode conf
		vmraid.conf.developer_mode = self._original_developer_flag

	def setUp(self):
		vmraid.flags.link_fields = {}
		super().setUp()

	def test_rename_doc(self):
		"""Rename an existing document via vmraid.rename_doc"""
		old_name = choice(self.available_documents)
		new_name = old_name + ".new"
		self.assertEqual(new_name, vmraid.rename_doc(self.test_doctype, old_name, new_name, force=True))
		self.available_documents.remove(old_name)
		self.available_documents.append(new_name)

	def test_merging_docs(self):
		"""Merge two documents via vmraid.rename_doc"""
		first_todo, second_todo = sample(self.available_documents, 2)

		second_todo_doc = vmraid.get_doc(self.test_doctype, second_todo)
		second_todo_doc.priority = "High"
		second_todo_doc.save()

		merged_todo = vmraid.rename_doc(
			self.test_doctype, first_todo, second_todo, merge=True, force=True
		)
		merged_todo_doc = vmraid.get_doc(self.test_doctype, merged_todo)
		self.available_documents.remove(first_todo)

		with self.assertRaises(DoesNotExistError):
			vmraid.get_doc(self.test_doctype, first_todo)

		self.assertEqual(merged_todo_doc.priority, second_todo_doc.priority)

	def test_rename_controllers(self):
		"""Rename doctypes with controller code paths"""
		# check if module exists exists;
		# if custom, get_controller will return Document class
		# if not custom, a different class will be returned
		self.assertNotEqual(get_controller(self.doctype.old), vmraid.model.document.Document)

		old_doctype_path = get_doc_path("Custom", "DocType", self.doctype.old)

		# rename doc via wrapper API accessible via /desk
		vmraid.rename_doc("DocType", self.doctype.old, self.doctype.new)

		# check if database and controllers are updated
		self.assertTrue(vmraid.db.exists("DocType", self.doctype.new))
		self.assertFalse(vmraid.db.exists("DocType", self.doctype.old))
		self.assertFalse(os.path.exists(old_doctype_path))

	def test_rename_doctype(self):
		"""Rename DocType via vmraid.rename_doc"""
		from vmraid.core.doctype.doctype.test_doctype import new_doctype

		if not vmraid.db.exists("DocType", "Rename This"):
			new_doctype(
				"Rename This",
				fields=[
					{
						"label": "Linked To",
						"fieldname": "linked_to_doctype",
						"fieldtype": "Link",
						"options": "DocType",
						"unique": 0,
					}
				],
			).insert()

		to_rename_record = vmraid.get_doc(
			{"doctype": "Rename This", "linked_to_doctype": "Rename This"}
		).insert()

		# Rename doctype
		self.assertEqual(
			"Renamed Doc", vmraid.rename_doc("DocType", "Rename This", "Renamed Doc", force=True)
		)

		# Test if Doctype value has changed in Link field
		linked_to_doctype = vmraid.db.get_value(
			"Renamed Doc", to_rename_record.name, "linked_to_doctype"
		)
		self.assertEqual(linked_to_doctype, "Renamed Doc")

		# Test if there are conflicts between a record and a DocType
		# having the same name
		old_name = to_rename_record.name
		new_name = "ToDo"
		self.assertEqual(
			new_name, vmraid.rename_doc("Renamed Doc", old_name, new_name, force=True)
		)

		# delete_doc doesnt drop tables
		# this is done to bypass inconsistencies in the db
		vmraid.delete_doc_if_exists("DocType", "Renamed Doc")
		vmraid.db.sql_ddl("drop table if exists `tabRenamed Doc`")
