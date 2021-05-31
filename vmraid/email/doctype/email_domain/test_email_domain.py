# -*- coding: utf-8 -*-
# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# See license.txt
from __future__ import unicode_literals

import vmraid
import unittest
from vmraid.test_runner import make_test_objects

test_records = vmraid.get_test_records('Email Domain')

class TestDomain(unittest.TestCase):

	def setUp(self):
		make_test_objects('Email Domain', reset=True)

	def tearDown(self):
		vmraid.delete_doc("Email Account", "Test")
		vmraid.delete_doc("Email Domain", "test.com")

	def test_on_update(self):
		mail_domain = vmraid.get_doc("Email Domain", "test.com")
		mail_account = vmraid.get_doc("Email Account", "Test")

		# Initially, incoming_port is different in domain and account
		self.assertNotEqual(mail_account.incoming_port, mail_domain.incoming_port)
		# Trigger update of accounts using this domain
		mail_domain.on_update()
		mail_account = vmraid.get_doc("Email Account", "Test")
		# After update, incoming_port in account should match the domain
		self.assertEqual(mail_account.incoming_port, mail_domain.incoming_port)

		# Also make sure that the other attributes match
		self.assertEqual(mail_account.use_imap, mail_domain.use_imap)
		self.assertEqual(mail_account.use_ssl, mail_domain.use_ssl)
		self.assertEqual(mail_account.use_tls, mail_domain.use_tls)
		self.assertEqual(mail_account.attachment_limit, mail_domain.attachment_limit)
		self.assertEqual(mail_account.smtp_server, mail_domain.smtp_server)
		self.assertEqual(mail_account.smtp_port, mail_domain.smtp_port)
