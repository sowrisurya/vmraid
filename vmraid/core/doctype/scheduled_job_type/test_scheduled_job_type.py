# -*- coding: utf-8 -*-
# Copyright (c) 2019, VMRaid Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import vmraid
import unittest
from vmraid.utils import get_datetime

from vmraid.core.doctype.scheduled_job_type.scheduled_job_type import sync_jobs

class TestScheduledJobType(unittest.TestCase):
	def setUp(self):
		vmraid.db.rollback()
		vmraid.db.sql('truncate `tabScheduled Job Type`')
		sync_jobs()
		vmraid.db.commit()

	def test_sync_jobs(self):
		all_job = vmraid.get_doc('Scheduled Job Type',
			dict(method='vmraid.email.queue.flush'))
		self.assertEqual(all_job.frequency, 'All')

		daily_job = vmraid.get_doc('Scheduled Job Type',
			dict(method='vmraid.email.queue.set_expiry_for_email_queue'))
		self.assertEqual(daily_job.frequency, 'Daily')

		# check if cron jobs are synced
		cron_job = vmraid.get_doc('Scheduled Job Type',
			dict(method='vmraid.oauth.delete_oauth2_data'))
		self.assertEqual(cron_job.frequency, 'Cron')
		self.assertEqual(cron_job.cron_format, '0/15 * * * *')

		# check if jobs are synced after change in hooks
		updated_scheduler_events = { "hourly": ["vmraid.email.queue.flush"] }
		sync_jobs(updated_scheduler_events)
		updated_scheduled_job = vmraid.get_doc("Scheduled Job Type", {"method": "vmraid.email.queue.flush"})
		self.assertEqual(updated_scheduled_job.frequency, "Hourly")

	def test_daily_job(self):
		job = vmraid.get_doc('Scheduled Job Type', dict(method = 'vmraid.email.queue.set_expiry_for_email_queue'))
		job.db_set('last_execution', '2019-01-01 00:00:00')
		self.assertTrue(job.is_event_due(get_datetime('2019-01-02 00:00:06')))
		self.assertFalse(job.is_event_due(get_datetime('2019-01-01 00:00:06')))
		self.assertFalse(job.is_event_due(get_datetime('2019-01-01 23:59:59')))

	def test_weekly_job(self):
		job = vmraid.get_doc('Scheduled Job Type', dict(method = 'vmraid.social.doctype.energy_point_log.energy_point_log.send_weekly_summary'))
		job.db_set('last_execution', '2019-01-01 00:00:00')
		self.assertTrue(job.is_event_due(get_datetime('2019-01-06 00:00:01')))
		self.assertFalse(job.is_event_due(get_datetime('2019-01-02 00:00:06')))
		self.assertFalse(job.is_event_due(get_datetime('2019-01-05 23:59:59')))

	def test_monthly_job(self):
		job = vmraid.get_doc('Scheduled Job Type', dict(method = 'vmraid.email.doctype.auto_email_report.auto_email_report.send_monthly'))
		job.db_set('last_execution', '2019-01-01 00:00:00')
		self.assertTrue(job.is_event_due(get_datetime('2019-02-01 00:00:01')))
		self.assertFalse(job.is_event_due(get_datetime('2019-01-15 00:00:06')))
		self.assertFalse(job.is_event_due(get_datetime('2019-01-31 23:59:59')))

	def test_cron_job(self):
		# runs every 15 mins
		job = vmraid.get_doc('Scheduled Job Type', dict(method = 'vmraid.oauth.delete_oauth2_data'))
		job.db_set('last_execution', '2019-01-01 00:00:00')
		self.assertTrue(job.is_event_due(get_datetime('2019-01-01 00:15:01')))
		self.assertFalse(job.is_event_due(get_datetime('2019-01-01 00:05:06')))
		self.assertFalse(job.is_event_due(get_datetime('2019-01-01 00:14:59')))
