#  -*- coding: utf-8 -*-
# Copyright (c) 2020, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import unittest
import vmraid
import vmraid.monitor
from vmraid.utils import set_request
from vmraid.utils.response import build_response
from vmraid.monitor import MONITOR_REDIS_KEY


class TestMonitor(unittest.TestCase):
	def setUp(self):
		vmraid.conf.monitor = 1
		vmraid.cache().delete_value(MONITOR_REDIS_KEY)

	def test_enable_monitor(self):
		set_request(method="GET", path="/api/method/vmraid.ping")
		response = build_response("json")

		vmraid.monitor.start()
		vmraid.monitor.stop(response)

		logs = vmraid.cache().lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)

		log = vmraid.parse_json(logs[0].decode())
		self.assertTrue(log.duration)
		self.assertTrue(log.site)
		self.assertTrue(log.timestamp)
		self.assertTrue(log.uuid)
		self.assertTrue(log.request)
		self.assertEqual(log.transaction_type, "request")
		self.assertEqual(log.request["method"], "GET")

	def test_job(self):
		vmraid.utils.background_jobs.execute_job(
			vmraid.local.site, "vmraid.ping", None, None, {}, is_async=False
		)

		logs = vmraid.cache().lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)
		log = vmraid.parse_json(logs[0].decode())
		self.assertEqual(log.transaction_type, "job")
		self.assertTrue(log.job)
		self.assertEqual(log.job["method"], "vmraid.ping")
		self.assertEqual(log.job["scheduled"], False)
		self.assertEqual(log.job["wait"], 0)

	def test_flush(self):
		set_request(method="GET", path="/api/method/vmraid.ping")
		response = build_response("json")
		vmraid.monitor.start()
		vmraid.monitor.stop(response)

		open(vmraid.monitor.log_file(), "w").close()
		vmraid.monitor.flush()

		with open(vmraid.monitor.log_file()) as f:
			logs = f.readlines()

		self.assertEqual(len(logs), 1)
		log = vmraid.parse_json(logs[0])
		self.assertEqual(log.transaction_type, "request")

	def tearDown(self):
		vmraid.conf.monitor = 0
		vmraid.cache().delete_value(MONITOR_REDIS_KEY)
