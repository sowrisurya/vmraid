# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# See license.txt
from __future__ import unicode_literals

import vmraid
import unittest, json

from vmraid.website.render import build_page
from vmraid.website.doctype.web_form.web_form import accept

test_dependencies = ['Web Form']

class TestWebForm(unittest.TestCase):
	def setUp(self):
		vmraid.conf.disable_website_cache = True
		vmraid.local.path = None

	def tearDown(self):
		vmraid.conf.disable_website_cache = False
		vmraid.local.path = None

	def test_accept(self):
		vmraid.set_user("Administrator")
		accept(web_form='manage-events', data=json.dumps({
			'doctype': 'Event',
			'subject': '_Test Event Web Form',
			'description': '_Test Event Description',
			'starts_on': '2014-09-09'
		}))

		self.event_name = vmraid.db.get_value("Event",
			{"subject": "_Test Event Web Form"})
		self.assertTrue(self.event_name)

	def test_edit(self):
		self.test_accept()
		doc={
			'doctype': 'Event',
			'subject': '_Test Event Web Form',
			'description': '_Test Event Description 1',
			'starts_on': '2014-09-09',
			'name': self.event_name
		}

		self.assertNotEqual(vmraid.db.get_value("Event",
			self.event_name, "description"), doc.get('description'))

		accept(web_form='manage-events', docname=self.event_name, data=json.dumps(doc))

		self.assertEqual(vmraid.db.get_value("Event",
			self.event_name, "description"), doc.get('description'))
