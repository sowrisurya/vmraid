# -*- coding: utf-8 -*-
# Copyright (c) 2017, VMRaid Technologies and Contributors
# See license.txt
from __future__ import unicode_literals
import vmraid, unittest

class TestDataMigrationRun(unittest.TestCase):
	def test_run(self):
		create_plan()

		description = 'data migration todo'
		new_todo = vmraid.get_doc({
			'doctype': 'ToDo',
			'description': description
		}).insert()

		event_subject = 'data migration event'
		vmraid.get_doc(dict(
			doctype='Event',
			subject=event_subject,
			repeat_on='Monthly',
			starts_on=vmraid.utils.now_datetime()
		)).insert()

		run = vmraid.get_doc({
			'doctype': 'Data Migration Run',
			'data_migration_plan': 'ToDo Sync',
			'data_migration_connector': 'Local Connector'
		}).insert()

		run.run()
		self.assertEqual(run.db_get('status'), 'Success')

		self.assertEqual(run.db_get('push_insert'), 1)
		self.assertEqual(run.db_get('pull_insert'), 1)

		todo = vmraid.get_doc('ToDo', new_todo.name)
		self.assertTrue(todo.todo_sync_id)

		# Pushed Event
		event = vmraid.get_doc('Event', todo.todo_sync_id)
		self.assertEqual(event.subject, description)

		# Pulled ToDo
		created_todo = vmraid.get_doc('ToDo', {'description': event_subject})
		self.assertEqual(created_todo.description, event_subject)

		todo_list = vmraid.get_list('ToDo', filters={'description': 'data migration todo'}, fields=['name'])
		todo_name = todo_list[0].name

		todo = vmraid.get_doc('ToDo', todo_name)
		todo.description = 'data migration todo updated'
		todo.save()

		run = vmraid.get_doc({
			'doctype': 'Data Migration Run',
			'data_migration_plan': 'ToDo Sync',
			'data_migration_connector': 'Local Connector'
		}).insert()

		run.run()

		# Update
		self.assertEqual(run.db_get('status'), 'Success')
		self.assertEqual(run.db_get('pull_update'), 1)

def create_plan():
	vmraid.get_doc({
		'doctype': 'Data Migration Mapping',
		'mapping_name': 'Todo to Event',
		'remote_objectname': 'Event',
		'remote_primary_key': 'name',
		'mapping_type': 'Push',
		'local_doctype': 'ToDo',
		'fields': [
			{ 'remote_fieldname': 'subject', 'local_fieldname': 'description' },
			{ 'remote_fieldname': 'starts_on', 'local_fieldname': 'eval:vmraid.utils.get_datetime_str(vmraid.utils.get_datetime())' }
		],
		'condition': '{"description": "data migration todo" }'
	}).insert(ignore_if_duplicate=True)

	vmraid.get_doc({
		'doctype': 'Data Migration Mapping',
		'mapping_name': 'Event to ToDo',
		'remote_objectname': 'Event',
		'remote_primary_key': 'name',
		'local_doctype': 'ToDo',
		'local_primary_key': 'name',
		'mapping_type': 'Pull',
		'condition': '{"subject": "data migration event" }',
		'fields': [
			{ 'remote_fieldname': 'subject', 'local_fieldname': 'description' }
		]
	}).insert(ignore_if_duplicate=True)

	vmraid.get_doc({
		'doctype': 'Data Migration Plan',
		'plan_name': 'ToDo Sync',
		'module': 'Core',
		'mappings': [
			{ 'mapping': 'Todo to Event' },
			{ 'mapping': 'Event to ToDo' }
		]
	}).insert(ignore_if_duplicate=True)

	vmraid.get_doc({
		'doctype': 'Data Migration Connector',
		'connector_name': 'Local Connector',
		'connector_type': 'VMRaid',
		# connect to same host.
		'hostname': vmraid.conf.host_name or vmraid.utils.get_site_url(vmraid.local.site),
		'username': 'Administrator',
		'password': vmraid.conf.get("admin_password") or 'admin'
	}).insert(ignore_if_duplicate=True)
