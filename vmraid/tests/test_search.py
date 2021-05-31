# Copyright (c) 2018, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import unittest
import vmraid
from vmraid.desk.search import search_link
from vmraid.desk.search import search_widget

class TestSearch(unittest.TestCase):
	def test_search_field_sanitizer(self):
		# pass
		search_link('DocType', 'User', query=None, filters=None, page_length=20, searchfield='name')
		result = vmraid.response['results'][0]
		self.assertTrue('User' in result['value'])

		#raise exception on injection
		self.assertRaises(vmraid.DataError,
			search_link, 'DocType', 'Customer', query=None, filters=None,
			page_length=20, searchfield='1=1')

		self.assertRaises(vmraid.DataError,
			search_link, 'DocType', 'Customer', query=None, filters=None,
			page_length=20, searchfield='select * from tabSessions) --')

		self.assertRaises(vmraid.DataError,
			search_link, 'DocType', 'Customer', query=None, filters=None,
			page_length=20, searchfield='name or (select * from tabSessions)')

		self.assertRaises(vmraid.DataError,
			search_link, 'DocType', 'Customer', query=None, filters=None,
			page_length=20, searchfield='*')

		self.assertRaises(vmraid.DataError,
			search_link, 'DocType', 'Customer', query=None, filters=None,
			page_length=20, searchfield=';')

		self.assertRaises(vmraid.DataError,
			search_link, 'DocType', 'Customer', query=None, filters=None,
			page_length=20, searchfield=';')

	#Search for the word "pay", part of the word "pays" (country) in french.
	def test_link_search_in_foreign_language(self):
		try:
			vmraid.local.lang = 'fr'
			search_widget(doctype="DocType", txt="pay", page_length=20)
			output = vmraid.response["values"]

			result = [['found' for x in y if x=="Country"] for y in output]
			self.assertTrue(['found'] in result)
		finally:
			vmraid.local.lang = 'en'

	def test_validate_and_sanitize_search_inputs(self):

		# should raise error if searchfield is injectable
		self.assertRaises(vmraid.DataError,
			get_data, *('User', 'Random', 'select * from tabSessions) --', '1', '10', dict()))

		# page_len and start should be converted to int
		self.assertListEqual(get_data('User', 'Random', 'email', 'name or (select * from tabSessions)', '10', dict()),
			['User', 'Random', 'email', 0, 10, {}])
		self.assertListEqual(get_data('User', 'Random', 'email', page_len='2', start='10', filters=dict()),
			['User', 'Random', 'email', 10, 2, {}])

		# DocType can be passed as None which should be accepted
		self.assertListEqual(get_data(None, 'Random', 'email', '2', '10', dict()),
			[None, 'Random', 'email', 2, 10, {}])

		# return empty string if passed doctype is invalid
		self.assertListEqual(get_data("Random DocType", 'Random', 'email', '2', '10', dict()), [])

		# should not fail if function is called via vmraid.call with extra arguments
		args = ("Random DocType", 'Random', 'email', '2', '10', dict())
		kwargs = {'as_dict': False}
		self.assertListEqual(vmraid.call('vmraid.tests.test_search.get_data', *args, **kwargs), [])

		# should not fail if query has @ symbol in it
		search_link('User', 'user@random', searchfield='name')
		self.assertListEqual(vmraid.response['results'], [])

@vmraid.validate_and_sanitize_search_inputs
def get_data(doctype, txt, searchfield, start, page_len, filters):
	return [doctype, txt, searchfield, start, page_len, filters]