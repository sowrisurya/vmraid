# -*- coding: utf-8 -*-
# Copyright (c) 2020, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

from datetime import datetime
import json
import traceback
import vmraid
import os
import uuid
import rq


MONITOR_REDIS_KEY = "monitor-transactions"
MONITOR_MAX_ENTRIES = 1000000


def start(transaction_type="request", method=None, kwargs=None):
	if vmraid.conf.monitor:
		vmraid.local.monitor = Monitor(transaction_type, method, kwargs)


def stop(response=None):
	if hasattr(vmraid.local, "monitor"):
		vmraid.local.monitor.dump(response)


def log_file():
	return os.path.join(vmraid.utils.get_bench_path(), "logs", "monitor.json.log")


class Monitor:
	def __init__(self, transaction_type, method, kwargs):
		try:
			self.data = vmraid._dict(
				{
					"site": vmraid.local.site,
					"timestamp": datetime.utcnow(),
					"transaction_type": transaction_type,
					"uuid": str(uuid.uuid4()),
				}
			)

			if transaction_type == "request":
				self.collect_request_meta()
			else:
				self.collect_job_meta(method, kwargs)
		except Exception:
			traceback.print_exc()

	def collect_request_meta(self):
		self.data.request = vmraid._dict(
			{
				"ip": vmraid.local.request_ip,
				"method": vmraid.request.method,
				"path": vmraid.request.path,
			}
		)

	def collect_job_meta(self, method, kwargs):
		self.data.job = vmraid._dict({"method": method, "scheduled": False, "wait": 0})
		if "run_scheduled_job" in method:
			self.data.job.method = kwargs["job_type"]
			self.data.job.scheduled = True

		job = rq.get_current_job()
		if job:
			self.data.uuid = job.id
			waitdiff = self.data.timestamp - job.enqueued_at
			self.data.job.wait = int(waitdiff.total_seconds() * 1000000)

	def dump(self, response=None):
		try:
			timediff = datetime.utcnow() - self.data.timestamp
			# Obtain duration in microseconds
			self.data.duration = int(timediff.total_seconds() * 1000000)

			if self.data.transaction_type == "request":
				self.data.request.status_code = response.status_code
				self.data.request.response_length = int(response.headers.get("Content-Length", 0))

				if hasattr(vmraid.local, "rate_limiter"):
					limiter = vmraid.local.rate_limiter
					self.data.request.counter = limiter.counter
					if limiter.rejected:
						self.data.request.reset = limiter.reset

			self.store()
		except Exception:
			traceback.print_exc()

	def store(self):
		if vmraid.cache().llen(MONITOR_REDIS_KEY) > MONITOR_MAX_ENTRIES:
			vmraid.cache().ltrim(MONITOR_REDIS_KEY, 1, -1)
		serialized = json.dumps(self.data, sort_keys=True, default=str)
		vmraid.cache().rpush(MONITOR_REDIS_KEY, serialized)


def flush():
	try:
		# Fetch all the logs without removing from cache
		logs = vmraid.cache().lrange(MONITOR_REDIS_KEY, 0, -1)
		if logs:
			logs = list(map(vmraid.safe_decode, logs))
			with open(log_file(), "a", os.O_NONBLOCK) as f:
				f.write("\n".join(logs))
				f.write("\n")
			# Remove fetched entries from cache
			vmraid.cache().ltrim(MONITOR_REDIS_KEY, len(logs) - 1, -1)
	except Exception:
		traceback.print_exc()
