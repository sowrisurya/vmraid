# -*- coding: utf-8 -*-
# Copyright (c) 2019, VMRaid Technologies and contributors
# For license information, please see license.txt

import json
from datetime import datetime
from typing import Dict, List

from croniter import croniter

import vmraid
from vmraid.model.document import Document
from vmraid.utils import get_datetime, now_datetime
from vmraid.utils.background_jobs import enqueue, get_jobs


class ScheduledJobType(Document):
	def autoname(self):
		self.name = ".".join(self.method.split(".")[-2:])

	def validate(self):
		if self.frequency != "All":
			# force logging for all events other than continuous ones (ALL)
			self.create_log = 1

	def enqueue(self, force=False):
		# enqueue event if last execution is done
		if self.is_event_due() or force:
			if vmraid.flags.enqueued_jobs:
				vmraid.flags.enqueued_jobs.append(self.method)

			if vmraid.flags.execute_job:
				self.execute()
			else:
				if not self.is_job_in_queue():
					enqueue('vmraid.core.doctype.scheduled_job_type.scheduled_job_type.run_scheduled_job',
						queue = self.get_queue_name(), job_type=self.method)
					return True

		return False

	def is_event_due(self, current_time = None):
		'''Return true if event is due based on time lapsed since last execution'''
		# if the next scheduled event is before NOW, then its due!
		return self.get_next_execution() <= (current_time or now_datetime())

	def is_job_in_queue(self):
		queued_jobs = get_jobs(site=vmraid.local.site, key='job_type')[vmraid.local.site]
		return self.method in queued_jobs

	def get_next_execution(self):
		CRON_MAP = {
			"Yearly": "0 0 1 1 *",
			"Annual": "0 0 1 1 *",
			"Monthly": "0 0 1 * *",
			"Monthly Long": "0 0 1 * *",
			"Weekly": "0 0 * * 0",
			"Weekly Long": "0 0 * * 0",
			"Daily": "0 0 * * *",
			"Daily Long": "0 0 * * *",
			"Hourly": "0 * * * *",
			"Hourly Long": "0 * * * *",
			"All": "0/" + str((vmraid.get_conf().scheduler_interval or 240) // 60) + " * * * *",
		}

		if not self.cron_format:
			self.cron_format = CRON_MAP[self.frequency]

		return croniter(self.cron_format,
			get_datetime(self.last_execution or datetime(2000, 1, 1))).get_next(datetime)

	def execute(self):
		self.scheduler_log = None
		try:
			self.log_status('Start')
			if self.server_script:
				script_name = vmraid.db.get_value("Server Script", self.server_script)
				if script_name:
					vmraid.get_doc('Server Script', script_name).execute_scheduled_method()
			else:
				vmraid.get_attr(self.method)()
			vmraid.db.commit()
			self.log_status('Complete')
		except Exception:
			vmraid.db.rollback()
			self.log_status('Failed')

	def log_status(self, status):
		# log file
		vmraid.logger("scheduler").info(f"Scheduled Job {status}: {self.method} for {vmraid.local.site}")
		self.update_scheduler_log(status)

	def update_scheduler_log(self, status):
		if not self.create_log:
			# self.get_next_execution will work properly iff self.last_execution is properly set
			if self.frequency == "All" and status == 'Start':
				self.db_set('last_execution', now_datetime(), update_modified=False)
				vmraid.db.commit()
			return
		if not self.scheduler_log:
			self.scheduler_log = vmraid.get_doc(dict(doctype = 'Scheduled Job Log', scheduled_job_type=self.name)).insert(ignore_permissions=True)
		self.scheduler_log.db_set('status', status)
		if status == 'Failed':
			self.scheduler_log.db_set('details', vmraid.get_traceback())
		if status == 'Start':
			self.db_set('last_execution', now_datetime(), update_modified=False)
		vmraid.db.commit()

	def get_queue_name(self):
		return 'long' if ('Long' in self.frequency) else 'default'

	def on_trash(self):
		vmraid.db.sql('delete from `tabScheduled Job Log` where scheduled_job_type=%s', self.name)


@vmraid.whitelist()
def execute_event(doc: str):
	vmraid.only_for("System Manager")
	doc = json.loads(doc)
	vmraid.get_doc("Scheduled Job Type", doc.get("name")).enqueue(force=True)
	return doc


def run_scheduled_job(job_type: str):
	"""This is a wrapper function that runs a hooks.scheduler_events method"""
	try:
		vmraid.get_doc("Scheduled Job Type", dict(method=job_type)).execute()
	except Exception:
		print(vmraid.get_traceback())


def sync_jobs(hooks: Dict = None):
	vmraid.reload_doc("core", "doctype", "scheduled_job_type")
	scheduler_events = hooks or vmraid.get_hooks("scheduler_events")
	all_events = insert_events(scheduler_events)
	clear_events(all_events)


def insert_events(scheduler_events: Dict) -> List:
	cron_jobs, event_jobs = [], []
	for event_type in scheduler_events:
		events = scheduler_events.get(event_type)
		if isinstance(events, dict):
			cron_jobs += insert_cron_jobs(events)
		else:
			# hourly, daily etc
			event_jobs += insert_event_jobs(events, event_type)
	return cron_jobs + event_jobs


def insert_cron_jobs(events: Dict) -> List:
	cron_jobs = []
	for cron_format in events:
		for event in events.get(cron_format):
			cron_jobs.append(event)
			insert_single_event("Cron", event, cron_format)
	return cron_jobs


def insert_event_jobs(events: List, event_type: str) -> List:
	event_jobs = []
	for event in events:
		event_jobs.append(event)
		frequency = event_type.replace("_", " ").title()
		insert_single_event(frequency, event)
	return event_jobs


def insert_single_event(frequency: str, event: str, cron_format: str = None):
	cron_expr = {"cron_format": cron_format} if cron_format else {}
	doc = vmraid.get_doc(
		{
			"doctype": "Scheduled Job Type",
			"method": event,
			"cron_format": cron_format,
			"frequency": frequency,
		}
	)

	if not vmraid.db.exists(
		"Scheduled Job Type", {"method": event, "frequency": frequency, **cron_expr}
	):
		try:
			doc.insert()
		except vmraid.DuplicateEntryError:
			doc.delete()
			doc.insert()


def clear_events(all_events: List):
	for event in vmraid.get_all(
		"Scheduled Job Type", fields=["name", "method", "server_script"]
	):
		is_server_script = event.server_script
		is_defined_in_hooks = event.method in all_events

		if not (is_defined_in_hooks or is_server_script):
			vmraid.delete_doc("Scheduled Job Type", event.name)
