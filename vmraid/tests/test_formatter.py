# -*- coding: utf-8 -*-
import vmraid
from vmraid import format
import unittest

class TestFormatter(unittest.TestCase):
	def test_currency_formatting(self):
		df = vmraid._dict({
			'fieldname': 'amount',
			'fieldtype': 'Currency',
			'options': 'currency'
		})

		doc = vmraid._dict({
			'amount': 5
		})
		vmraid.db.set_default("currency", 'INR')

		# if currency field is not passed then default currency should be used.
		self.assertEqual(format(100, df, doc), '₹ 100.00')

		doc.currency = 'USD'
		self.assertEqual(format(100, df, doc), "$ 100.00")

		vmraid.db.set_default("currency", None)