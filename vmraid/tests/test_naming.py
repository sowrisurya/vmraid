# Copyright (c) 2018, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import unittest
import vmraid
from vmraid.utils import now_datetime

from vmraid.model.naming import getseries
from vmraid.model.naming import append_number_if_name_exists, revert_series_if_last

class TestNaming(unittest.TestCase):
	def tearDown(self):
		# Reset ToDo autoname to hash
		todo_doctype = vmraid.get_doc('DocType', 'ToDo')
		todo_doctype.autoname = 'hash'
		todo_doctype.save()

	def test_append_number_if_name_exists(self):
		'''
		Append number to name based on existing values
		if Bottle exists
			Bottle -> Bottle-1
		if Bottle-1 exists
			Bottle -> Bottle-2
		'''

		note = vmraid.new_doc('Note')
		note.title = 'Test'
		note.insert()

		title2 = append_number_if_name_exists('Note', 'Test')
		self.assertEqual(title2, 'Test-1')

		title2 = append_number_if_name_exists('Note', 'Test', 'title', '_')
		self.assertEqual(title2, 'Test_1')

	def test_format_autoname(self):
		'''
		Test if braced params are replaced in format autoname
		'''
		doctype = 'ToDo'

		todo_doctype = vmraid.get_doc('DocType', doctype)
		todo_doctype.autoname = 'format:TODO-{MM}-{status}-{##}'
		todo_doctype.save()

		description = 'Format'

		todo = vmraid.new_doc(doctype)
		todo.description = description
		todo.insert()

		series = getseries('', 2)

		series = str(int(series)-1)

		if len(series) < 2:
			series = '0' + series

		self.assertEqual(todo.name, 'TODO-{month}-{status}-{series}'.format(
			month=now_datetime().strftime('%m'), status=todo.status, series=series))

	def test_revert_series(self):
		from datetime import datetime
		year = datetime.now().year

		series = 'TEST-{}-'.format(year)
		key = 'TEST-.YYYY.-'
		name = 'TEST-{}-00001'.format(year)
		vmraid.db.sql("""INSERT INTO `tabSeries` (name, current) values (%s, 1)""", (series,))
		revert_series_if_last(key, name)
		current_index = vmraid.db.sql("""SELECT current from `tabSeries` where name = %s""", series, as_dict=True)[0]

		self.assertEqual(current_index.get('current'), 0)
		vmraid.db.sql("""delete from `tabSeries` where name = %s""", series)

		series = 'TEST-{}-'.format(year)
		key = 'TEST-.YYYY.-.#####'
		name = 'TEST-{}-00002'.format(year)
		vmraid.db.sql("""INSERT INTO `tabSeries` (name, current) values (%s, 2)""", (series,))
		revert_series_if_last(key, name)
		current_index = vmraid.db.sql("""SELECT current from `tabSeries` where name = %s""", series, as_dict=True)[0]

		self.assertEqual(current_index.get('current'), 1)
		vmraid.db.sql("""delete from `tabSeries` where name = %s""", series)

		series = 'TEST-'
		key = 'TEST-'
		name = 'TEST-00003'
		vmraid.db.sql("DELETE FROM `tabSeries` WHERE `name`=%s", series)
		vmraid.db.sql("""INSERT INTO `tabSeries` (name, current) values (%s, 3)""", (series,))
		revert_series_if_last(key, name)
		current_index = vmraid.db.sql("""SELECT current from `tabSeries` where name = %s""", series, as_dict=True)[0]

		self.assertEqual(current_index.get('current'), 2)
		vmraid.db.sql("""delete from `tabSeries` where name = %s""", series)

		series = 'TEST1-'
		key = 'TEST1-.#####.-2021-22'
		name = 'TEST1-00003-2021-22'
		vmraid.db.sql("DELETE FROM `tabSeries` WHERE `name`=%s", series)
		vmraid.db.sql("""INSERT INTO `tabSeries` (name, current) values (%s, 3)""", (series,))
		revert_series_if_last(key, name)
		current_index = vmraid.db.sql("""SELECT current from `tabSeries` where name = %s""", series, as_dict=True)[0]

		self.assertEqual(current_index.get('current'), 2)
		vmraid.db.sql("""delete from `tabSeries` where name = %s""", series)

		series = ''
		key = '.#####.-2021-22'
		name = '00003-2021-22'
		vmraid.db.sql("DELETE FROM `tabSeries` WHERE `name`=%s", series)
		vmraid.db.sql("""INSERT INTO `tabSeries` (name, current) values (%s, 3)""", (series,))
		revert_series_if_last(key, name)
		current_index = vmraid.db.sql("""SELECT current from `tabSeries` where name = %s""", series, as_dict=True)[0]

		self.assertEqual(current_index.get('current'), 2)
		vmraid.db.sql("""delete from `tabSeries` where name = %s""", series)
