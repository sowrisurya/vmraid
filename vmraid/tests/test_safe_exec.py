from __future__ import unicode_literals
import unittest, vmraid
from vmraid.utils.safe_exec import safe_exec, get_safe_globals

class TestSafeExec(unittest.TestCase):
	def test_import_fails(self):
		self.assertRaises(ImportError, safe_exec, 'import os')

	def test_internal_attributes(self):
		self.assertRaises(SyntaxError, safe_exec, '().__class__.__call__')

	def test_utils(self):
		_locals = dict(out=None)
		safe_exec('''out = vmraid.utils.cint("1")''', None, _locals)
		self.assertEqual(_locals['out'], 1)

	def test_safe_eval(self):
		self.assertEqual(vmraid.safe_eval('1+1'), 2)
		self.assertRaises(AttributeError, vmraid.safe_eval, 'vmraid.utils.os.path', get_safe_globals())

	def test_sql(self):
		_locals = dict(out=None)
		safe_exec('''out = vmraid.db.sql("select name from tabDocType where name='DocType'")''', None, _locals)
		self.assertEqual(_locals['out'][0][0], 'DocType')

		self.assertRaises(vmraid.PermissionError, safe_exec, 'vmraid.db.sql("update tabToDo set description=NULL")')