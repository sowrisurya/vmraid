#  -*- coding: utf-8 -*-

# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# See license.txt

from __future__ import unicode_literals

import vmraid
import unittest

test_records = vmraid.get_test_records('Custom Field')

class TestCustomField(unittest.TestCase):
	pass
