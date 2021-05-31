# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# See license.txt
from __future__ import unicode_literals

import vmraid
import unittest

test_records = vmraid.get_test_records('Page')

class TestPage(unittest.TestCase):
	def test_naming(self):
		self.assertRaises(vmraid.NameError, vmraid.get_doc(dict(doctype='Page', page_name='DocType', module='Core')).insert)
		self.assertRaises(vmraid.NameError, vmraid.get_doc(dict(doctype='Page', page_name='Settings', module='Core')).insert)
