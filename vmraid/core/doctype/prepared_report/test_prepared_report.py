# -*- coding: utf-8 -*-
# Copyright (c) 2018, VMRaid Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import vmraid
import unittest
import json


class TestPreparedReport(unittest.TestCase):
	def setUp(self):
		self.report = vmraid.get_doc({
			"doctype": "Report",
			"name": "Permitted Documents For User"
		})
		self.filters = {
			"user": "Administrator",
			"doctype": "Role"
		}
		self.prepared_report_doc = vmraid.get_doc({
			"doctype": "Prepared Report",
			"report_name": self.report.name,
			"filters": json.dumps(self.filters),
			"ref_report_doctype": self.report.name
		}).insert()

	def tearDown(self):
		vmraid.set_user("Administrator")
		self.prepared_report_doc.delete()

	def test_for_creation(self):
		self.assertTrue('QUEUED' == self.prepared_report_doc.status.upper())
		self.assertTrue(self.prepared_report_doc.report_start_time)
