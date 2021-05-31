# -*- coding: utf-8 -*-
# Copyright (c) 2015, VMRaid Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import vmraid
import unittest
import time
from vmraid.auth import LoginManager, CookieManager

class TestActivityLog(unittest.TestCase):
	def test_activity_log(self):

		# test user login log
		vmraid.local.form_dict = vmraid._dict({
			'cmd': 'login',
			'sid': 'Guest',
			'pwd': 'admin',
			'usr': 'Administrator'
		})

		vmraid.local.cookie_manager = CookieManager()
		vmraid.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, 'Success')

		# test user logout log
		vmraid.local.login_manager.logout()
		auth_log = self.get_auth_log(operation='Logout')
		self.assertEqual(auth_log.status, 'Success')

		# test invalid login
		vmraid.form_dict.update({ 'pwd': 'password' })
		self.assertRaises(vmraid.AuthenticationError, LoginManager)
		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, 'Failed')

		vmraid.local.form_dict = vmraid._dict()

	def get_auth_log(self, operation='Login'):
		names = vmraid.db.get_all('Activity Log', filters={
			'user': 'Administrator',
			'operation': operation,
		}, order_by='`creation` DESC')

		name = names[0]
		auth_log = vmraid.get_doc('Activity Log', name)
		return auth_log

	def test_brute_security(self):
		update_system_settings({
			'allow_consecutive_login_attempts': 3,
			'allow_login_after_fail': 5
		})

		vmraid.local.form_dict = vmraid._dict({
			'cmd': 'login',
			'sid': 'Guest',
			'pwd': 'admin',
			'usr': 'Administrator'
		})

		vmraid.local.cookie_manager = CookieManager()
		vmraid.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, 'Success')

		# test user logout log
		vmraid.local.login_manager.logout()
		auth_log = self.get_auth_log(operation='Logout')
		self.assertEqual(auth_log.status, 'Success')

		# test invalid login
		vmraid.form_dict.update({ 'pwd': 'password' })
		self.assertRaises(vmraid.AuthenticationError, LoginManager)
		self.assertRaises(vmraid.AuthenticationError, LoginManager)
		self.assertRaises(vmraid.AuthenticationError, LoginManager)

		# REMOVE ME: current logic allows allow_consecutive_login_attempts+1 attempts
		# before raising security exception, remove below line when that is fixed.
		self.assertRaises(vmraid.AuthenticationError, LoginManager)
		self.assertRaises(vmraid.SecurityException, LoginManager)
		time.sleep(5)
		self.assertRaises(vmraid.AuthenticationError, LoginManager)

		vmraid.local.form_dict = vmraid._dict()

def update_system_settings(args):
	doc = vmraid.get_doc('System Settings')
	doc.update(args)
	doc.flags.ignore_mandatory = 1
	doc.save()
