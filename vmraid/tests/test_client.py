# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors

from __future__ import unicode_literals

import unittest
import vmraid


class TestClient(unittest.TestCase):
	def test_set_value(self):
		todo = vmraid.get_doc(dict(doctype='ToDo', description='test')).insert()
		vmraid.set_value('ToDo', todo.name, 'description', 'test 1')
		self.assertEqual(vmraid.get_value('ToDo', todo.name, 'description'), 'test 1')

		vmraid.set_value('ToDo', todo.name, {'description': 'test 2'})
		self.assertEqual(vmraid.get_value('ToDo', todo.name, 'description'), 'test 2')

	def test_delete(self):
		from vmraid.client import delete

		todo = vmraid.get_doc(dict(doctype='ToDo', description='description')).insert()
		delete("ToDo", todo.name)

		self.assertFalse(vmraid.db.exists("ToDo", todo.name))
		self.assertRaises(vmraid.DoesNotExistError, delete, "ToDo", todo.name)

	def test_http_valid_method_access(self):
		from vmraid.client import delete
		from vmraid.handler import execute_cmd

		vmraid.set_user("Administrator")

		vmraid.local.request = vmraid._dict()
		vmraid.local.request.method = 'POST'

		vmraid.local.form_dict = vmraid._dict({
			'doc': dict(doctype='ToDo', description='Valid http method'),
			'cmd': 'vmraid.client.save'
		})
		todo = execute_cmd('vmraid.client.save')

		self.assertEqual(todo.get('description'), 'Valid http method')

		delete("ToDo", todo.name)

	def test_http_invalid_method_access(self):
		from vmraid.handler import execute_cmd

		vmraid.set_user("Administrator")

		vmraid.local.request = vmraid._dict()
		vmraid.local.request.method = 'GET'

		vmraid.local.form_dict = vmraid._dict({
			'doc': dict(doctype='ToDo', description='Invalid http method'),
			'cmd': 'vmraid.client.save'
		})

		self.assertRaises(vmraid.PermissionError, execute_cmd, 'vmraid.client.save')

	def test_run_doc_method(self):
		from vmraid.handler import execute_cmd

		if not vmraid.db.exists('Report', 'Test Run Doc Method'):
			report = vmraid.get_doc({
				'doctype': 'Report',
				'ref_doctype': 'User',
				'report_name': 'Test Run Doc Method',
				'report_type': 'Query Report',
				'is_standard': 'No',
				'roles': [
					{'role': 'System Manager'}
				]
			}).insert()
		else:
			report = vmraid.get_doc('Report', 'Test Run Doc Method')

		vmraid.local.request = vmraid._dict()
		vmraid.local.request.method = 'GET'

		# Whitelisted, works as expected
		vmraid.local.form_dict = vmraid._dict({
			'dt': report.doctype,
			'dn': report.name,
			'method': 'toggle_disable',
			'cmd': 'run_doc_method',
			'args': 0
		})

		execute_cmd(vmraid.local.form_dict.cmd)

		# Not whitelisted, throws permission error
		vmraid.local.form_dict = vmraid._dict({
			'dt': report.doctype,
			'dn': report.name,
			'method': 'create_report_py',
			'cmd': 'run_doc_method',
			'args': 0
		})

		self.assertRaises(
			vmraid.PermissionError,
			execute_cmd,
			vmraid.local.form_dict.cmd
		)
