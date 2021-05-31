# -*- coding: utf-8 -*-
# Copyright (c) 2019, VMRaid Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import vmraid
import unittest
import requests
from vmraid.utils import get_site_url

scripts = [
	dict(
		name='test_todo',
		script_type = 'DocType Event',
		doctype_event = 'Before Insert',
		reference_doctype = 'ToDo',
		script = '''
if "test" in doc.description:
	doc.status = 'Closed'
'''
	),
	dict(
		name='test_todo_validate',
		script_type = 'DocType Event',
		doctype_event = 'Before Insert',
		reference_doctype = 'ToDo',
		script = '''
if "validate" in doc.description:
	raise vmraid.ValidationError
'''
	),
	dict(
		name='test_api',
		script_type = 'API',
		api_method = 'test_server_script',
		allow_guest = 1,
		script = '''
vmraid.response['message'] = 'hello'
'''
	),
	dict(
		name='test_return_value',
		script_type = 'API',
		api_method = 'test_return_value',
		allow_guest = 1,
		script = '''
vmraid.flags = 'hello'
'''
	),
	dict(
		name='test_permission_query',
		script_type = 'Permission Query',
		reference_doctype = 'ToDo',
		script = '''
conditions = '1 = 1'
'''),
  dict(
		name='test_invalid_namespace_method',
		script_type = 'DocType Event',
		doctype_event = 'Before Insert',
		reference_doctype = 'Note',
		script = '''
vmraid.method_that_doesnt_exist("do some magic")
'''
	)
]
class TestServerScript(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		vmraid.db.commit()
		vmraid.db.sql('truncate `tabServer Script`')
		vmraid.get_doc('User', 'Administrator').add_roles('Script Manager')
		for script in scripts:
			script_doc = vmraid.get_doc(doctype ='Server Script')
			script_doc.update(script)
			script_doc.insert()

		vmraid.db.commit()

	@classmethod
	def tearDownClass(cls):
		vmraid.db.commit()
		vmraid.db.sql('truncate `tabServer Script`')
		vmraid.cache().delete_value('server_script_map')

	def setUp(self):
		vmraid.cache().delete_value('server_script_map')

	def test_doctype_event(self):
		todo = vmraid.get_doc(dict(doctype='ToDo', description='hello')).insert()
		self.assertEqual(todo.status, 'Open')

		todo = vmraid.get_doc(dict(doctype='ToDo', description='test todo')).insert()
		self.assertEqual(todo.status, 'Closed')

		self.assertRaises(vmraid.ValidationError, vmraid.get_doc(dict(doctype='ToDo', description='validate me')).insert)

	def test_api(self):
		response = requests.post(get_site_url(vmraid.local.site) + "/api/method/test_server_script")
		self.assertEqual(response.status_code, 200)
		self.assertEqual("hello", response.json()["message"])

	def test_api_return(self):
		self.assertEqual(vmraid.get_doc('Server Script', 'test_return_value').execute_method(), 'hello')

	def test_permission_query(self):
		self.assertTrue('where (1 = 1)' in vmraid.db.get_list('ToDo', return_query=1))
		self.assertTrue(isinstance(vmraid.db.get_list('ToDo'), list))

	def test_attribute_error(self):
		"""Raise AttributeError if method not found in Namespace"""
		note = vmraid.get_doc({"doctype": "Note", "title": "Test Note: Server Script"})
		self.assertRaises(AttributeError, note.insert)
