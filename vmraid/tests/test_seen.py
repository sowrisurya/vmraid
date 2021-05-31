# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import vmraid, unittest, json

class TestSeen(unittest.TestCase):
	def tearDown(self):
		vmraid.set_user('Administrator')

	def test_if_user_is_added(self):
		ev = vmraid.get_doc({
			'doctype': 'Event',
			'subject': 'test event for seen',
			'starts_on': '2016-01-01 10:10:00',
			'event_type': 'Public'
		}).insert()

		vmraid.set_user('test@example.com')

		from vmraid.desk.form.load import getdoc

		# load the form
		getdoc('Event', ev.name)

		# reload the event
		ev = vmraid.get_doc('Event', ev.name)

		self.assertTrue('test@example.com' in json.loads(ev._seen))

		# test another user
		vmraid.set_user('test1@example.com')

		# load the form
		getdoc('Event', ev.name)

		# reload the event
		ev = vmraid.get_doc('Event', ev.name)

		self.assertTrue('test@example.com' in json.loads(ev._seen))
		self.assertTrue('test1@example.com' in json.loads(ev._seen))

		ev.save()
		ev = vmraid.get_doc('Event', ev.name)

		self.assertFalse('test@example.com' in json.loads(ev._seen))
		self.assertTrue('test1@example.com' in json.loads(ev._seen))
