#  -*- coding: utf-8 -*-

# Copyright (c) 2019, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import unittest
import vmraid
import vmraid.recorder
from vmraid.utils import set_request
from vmraid.website.render import render_page

import sqlparse

class TestRecorder(unittest.TestCase):
	def setUp(self):
		vmraid.recorder.stop()
		vmraid.recorder.delete()
		set_request()
		vmraid.recorder.start()
		vmraid.recorder.record()

	def test_start(self):
		vmraid.recorder.dump()
		requests = vmraid.recorder.get()
		self.assertEqual(len(requests), 1)

	def test_do_not_record(self):
		vmraid.recorder.do_not_record(vmraid.get_all)('DocType')
		vmraid.recorder.dump()
		requests = vmraid.recorder.get()
		self.assertEqual(len(requests), 0)

	def test_get(self):
		vmraid.recorder.dump()

		requests = vmraid.recorder.get()
		self.assertEqual(len(requests), 1)

		request = vmraid.recorder.get(requests[0]['uuid'])
		self.assertTrue(request)

	def test_delete(self):
		vmraid.recorder.dump()

		requests = vmraid.recorder.get()
		self.assertEqual(len(requests), 1)

		vmraid.recorder.delete()

		requests = vmraid.recorder.get()
		self.assertEqual(len(requests), 0)

	def test_record_without_sql_queries(self):
		vmraid.recorder.dump()

		requests = vmraid.recorder.get()
		request = vmraid.recorder.get(requests[0]['uuid'])

		self.assertEqual(len(request['calls']), 0)

	def test_record_with_sql_queries(self):
		vmraid.get_all('DocType')
		vmraid.recorder.dump()

		requests = vmraid.recorder.get()
		request = vmraid.recorder.get(requests[0]['uuid'])

		self.assertNotEqual(len(request['calls']), 0)

	def test_explain(self):
		vmraid.db.sql('SELECT * FROM tabDocType')
		vmraid.db.sql('COMMIT')
		vmraid.recorder.dump()

		requests = vmraid.recorder.get()
		request = vmraid.recorder.get(requests[0]['uuid'])

		self.assertEqual(len(request['calls'][0]['explain_result']), 1)
		self.assertEqual(len(request['calls'][1]['explain_result']), 0)


	def test_multiple_queries(self):
		queries = [
			{'mariadb': 'SELECT * FROM tabDocType', 'postgres': 'SELECT * FROM "tabDocType"'},
			{'mariadb': 'SELECT COUNT(*) FROM tabDocType', 'postgres': 'SELECT COUNT(*) FROM "tabDocType"'},
			{'mariadb': 'COMMIT', 'postgres': 'COMMIT'},
		]

		sql_dialect = vmraid.db.db_type or 'mariadb'
		for query in queries:
			vmraid.db.sql(query[sql_dialect])

		vmraid.recorder.dump()

		requests = vmraid.recorder.get()
		request = vmraid.recorder.get(requests[0]['uuid'])

		self.assertEqual(len(request['calls']), len(queries))

		for query, call in zip(queries, request['calls']):
			self.assertEqual(call['query'], sqlparse.format(query[sql_dialect].strip(), keyword_case='upper', reindent=True))

	def test_duplicate_queries(self):
		queries = [
			('SELECT * FROM tabDocType', 2),
			('SELECT COUNT(*) FROM tabDocType', 1),
			('select * from tabDocType', 2),
			('COMMIT', 3),
			('COMMIT', 3),
			('COMMIT', 3),
		]
		for query in queries:
			vmraid.db.sql(query[0])

		vmraid.recorder.dump()

		requests = vmraid.recorder.get()
		request = vmraid.recorder.get(requests[0]['uuid'])

		for query, call in zip(queries, request['calls']):
			self.assertEqual(call['exact_copies'], query[1])

	def test_error_page_rendering(self):
		content = render_page("error")
		self.assertIn("Error", content)
