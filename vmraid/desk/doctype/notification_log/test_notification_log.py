# -*- coding: utf-8 -*-
# Copyright (c) 2019, VMRaid Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import vmraid
from vmraid.desk.form.assign_to import add as assign_task
import unittest

class TestNotificationLog(unittest.TestCase):
	def test_assignment(self):
		todo = get_todo()
		user = get_user()

		assign_task({
			"assign_to": [user],
			"doctype": 'ToDo',
			"name": todo.name,
			"description": todo.description
		})
		log_type = vmraid.db.get_value('Notification Log', {
			'document_type': 'ToDo',
			'document_name': todo.name
		}, 'type')
		self.assertEqual(log_type, 'Assignment')

	def test_share(self):
		todo = get_todo()
		user = get_user()

		vmraid.share.add('ToDo', todo.name, user, notify=1)
		log_type = vmraid.db.get_value('Notification Log', {
			'document_type': 'ToDo',
			'document_name': todo.name
		}, 'type')
		self.assertEqual(log_type, 'Share')

		email = get_last_email_queue()
		content = 'Subject: {} shared a document ToDo'.format(vmraid.utils.get_fullname(vmraid.session.user))
		self.assertTrue(content in email.message)


def get_last_email_queue():
	res = vmraid.db.get_all('Email Queue',
		fields=['message'],
		order_by='creation desc',
		limit=1
	)
	return res[0]

def get_todo():
	if not vmraid.get_all('ToDo'):
		return vmraid.get_doc({ 'doctype': 'ToDo', 'description': 'Test for Notification' }).insert()

	res = vmraid.get_all('ToDo', limit=1)
	return vmraid.get_cached_doc('ToDo', res[0].name)

def get_user():
	users = vmraid.db.get_all('User',
		filters={'name': ('not in', ['Administrator', 'Guest'])},
		fields='name', limit=1)
	return users[0].name
