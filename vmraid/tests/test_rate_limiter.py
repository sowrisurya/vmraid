#  -*- coding: utf-8 -*-

# Copyright (c) 2020, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import unittest
from werkzeug.wrappers import Response
import time

import vmraid
import vmraid.rate_limiter
from vmraid.rate_limiter import RateLimiter
from vmraid.utils import cint


class TestRateLimiter(unittest.TestCase):
	def setUp(self):
		pass

	def test_apply_with_limit(self):
		vmraid.conf.rate_limit = {"window": 86400, "limit": 1}
		vmraid.rate_limiter.apply()

		self.assertTrue(hasattr(vmraid.local, "rate_limiter"))
		self.assertIsInstance(vmraid.local.rate_limiter, RateLimiter)

		vmraid.cache().delete(vmraid.local.rate_limiter.key)
		delattr(vmraid.local, "rate_limiter")

	def test_apply_without_limit(self):
		vmraid.conf.rate_limit = None
		vmraid.rate_limiter.apply()

		self.assertFalse(hasattr(vmraid.local, "rate_limiter"))

	def test_respond_over_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		vmraid.conf.rate_limit = {"window": 86400, "limit": 0.01}
		self.assertRaises(vmraid.TooManyRequestsError, vmraid.rate_limiter.apply)
		vmraid.rate_limiter.update()

		response = vmraid.rate_limiter.respond()

		self.assertIsInstance(response, Response)
		self.assertEqual(response.status_code, 429)

		headers = vmraid.local.rate_limiter.headers()
		self.assertIn("Retry-After", headers)
		self.assertNotIn("X-RateLimit-Used", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertIn("X-RateLimit-Limit", headers)
		self.assertIn("X-RateLimit-Remaining", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"]) <= 86400)
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 10000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 0)

		vmraid.cache().delete(limiter.key)
		vmraid.cache().delete(vmraid.local.rate_limiter.key)
		delattr(vmraid.local, "rate_limiter")

	def test_respond_under_limit(self):
		vmraid.conf.rate_limit = {"window": 86400, "limit": 0.01}
		vmraid.rate_limiter.apply()
		vmraid.rate_limiter.update()
		response = vmraid.rate_limiter.respond()
		self.assertEqual(response, None)

		vmraid.cache().delete(vmraid.local.rate_limiter.key)
		delattr(vmraid.local, "rate_limiter")

	def test_headers_under_limit(self):
		vmraid.conf.rate_limit = {"window": 86400, "limit": 0.01}
		vmraid.rate_limiter.apply()
		vmraid.rate_limiter.update()
		headers = vmraid.local.rate_limiter.headers()
		self.assertNotIn("Retry-After", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"] < 86400))
		self.assertEqual(int(headers["X-RateLimit-Used"]), vmraid.local.rate_limiter.duration)
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 10000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 10000)

		vmraid.cache().delete(vmraid.local.rate_limiter.key)
		delattr(vmraid.local, "rate_limiter")

	def test_reject_over_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.01, 86400)
		self.assertRaises(vmraid.TooManyRequestsError, limiter.apply)

		vmraid.cache().delete(limiter.key)

	def test_do_not_reject_under_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.02, 86400)
		self.assertEqual(limiter.apply(), None)

		vmraid.cache().delete(limiter.key)

	def test_update_method(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		self.assertEqual(limiter.duration, cint(vmraid.cache().get(limiter.key)))

		vmraid.cache().delete(limiter.key)
