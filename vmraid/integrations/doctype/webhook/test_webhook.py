# -*- coding: utf-8 -*-
# Copyright (c) 2017, VMRaid Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import unittest

import vmraid
from vmraid.integrations.doctype.webhook.webhook import get_webhook_headers, get_webhook_data


class TestWebhook(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		# delete any existing webhooks
		vmraid.db.sql("DELETE FROM tabWebhook")
		# create test webhooks
		cls.create_sample_webhooks()

	@classmethod
	def create_sample_webhooks(cls):
		samples_webhooks_data = [
			{
				"webhook_doctype": "User",
				"webhook_docevent": "after_insert",
				"request_url": "https://httpbin.org/post",
				"condition": "doc.email",
				"enabled": True
			},
			{
				"webhook_doctype": "User",
				"webhook_docevent": "after_insert",
				"request_url": "https://httpbin.org/post",
				"condition": "doc.first_name",
				"enabled": False
			}
		]

		cls.sample_webhooks = []
		for wh_fields in samples_webhooks_data:
			wh = vmraid.new_doc("Webhook")
			wh.update(wh_fields)
			wh.insert()
			cls.sample_webhooks.append(wh)

	@classmethod
	def tearDownClass(cls):
		# delete any existing webhooks
		vmraid.db.sql("DELETE FROM tabWebhook")

	def setUp(self):
		# retrieve or create a User webhook for `after_insert`
		webhook_fields = {
			"webhook_doctype": "User",
			"webhook_docevent": "after_insert",
			"request_url": "https://httpbin.org/post"
		}

		if vmraid.db.exists("Webhook", webhook_fields):
			self.webhook = vmraid.get_doc("Webhook", webhook_fields)
		else:
			self.webhook = vmraid.new_doc("Webhook")
			self.webhook.update(webhook_fields)

		# create a User document
		self.user = vmraid.new_doc("User")
		self.user.first_name = vmraid.mock("name")
		self.user.email = vmraid.mock("email")
		self.user.save()

		# Create another test user specific to this test
		self.test_user = vmraid.new_doc("User")
		self.test_user.email = "user1@integration.webhooks.test.com"
		self.test_user.first_name = "user1"

	def tearDown(self) -> None:
		self.user.delete()
		self.test_user.delete()
		super().tearDown()

	def test_webhook_trigger_with_enabled_webhooks(self):
		"""Test webhook trigger for enabled webhooks"""

		vmraid.cache().delete_value('webhooks')
		vmraid.flags.webhooks = None

		# Insert the user to db
		self.test_user.insert()
		
		self.assertTrue("User" in vmraid.flags.webhooks)
		# only 1 hook (enabled) must be queued
		self.assertEqual(
			len(vmraid.flags.webhooks.get("User")),
			1
		)
		self.assertTrue(self.test_user.email in vmraid.flags.webhooks_executed)
		self.assertEqual(
			vmraid.flags.webhooks_executed.get(self.test_user.email)[0], 
			self.sample_webhooks[0].name
		)

	def test_validate_doc_events(self):
		"Test creating a submit-related webhook for a non-submittable DocType"

		self.webhook.webhook_docevent = "on_submit"
		self.assertRaises(vmraid.ValidationError, self.webhook.save)

	def test_validate_request_url(self):
		"Test validation for the webhook request URL"

		self.webhook.request_url = "httpbin.org?post"
		self.assertRaises(vmraid.ValidationError, self.webhook.save)

	def test_validate_headers(self):
		"Test validation for request headers"

		# test incomplete headers
		self.webhook.set("webhook_headers", [{
			"key": "Content-Type"
		}])
		self.webhook.save()
		headers = get_webhook_headers(doc=None, webhook=self.webhook)
		self.assertEqual(headers, {})

		# test complete headers
		self.webhook.set("webhook_headers", [{
			"key": "Content-Type",
			"value": "application/json"
		}])
		self.webhook.save()
		headers = get_webhook_headers(doc=None, webhook=self.webhook)
		self.assertEqual(headers, {"Content-Type": "application/json"})

	def test_validate_request_body_form(self):
		"Test validation of Form URL-Encoded request body"

		self.webhook.request_structure = "Form URL-Encoded"
		self.webhook.set("webhook_data", [{
			"fieldname": "name",
			"key": "name"
		}])
		self.webhook.webhook_json = """{
			"name": "{{ doc.name }}"
		}"""
		self.webhook.save()
		self.assertEqual(self.webhook.webhook_json, None)

		data = get_webhook_data(doc=self.user, webhook=self.webhook)
		self.assertEqual(data, {"name": self.user.name})

	def test_validate_request_body_json(self):
		"Test validation of JSON request body"

		self.webhook.request_structure = "JSON"
		self.webhook.set("webhook_data", [{
			"fieldname": "name",
			"key": "name"
		}])
		self.webhook.webhook_json = """{
			"name": "{{ doc.name }}"
		}"""
		self.webhook.save()
		self.assertEqual(self.webhook.webhook_data, [])

		data = get_webhook_data(doc=self.user, webhook=self.webhook)
		self.assertEqual(data, {"name": self.user.name})
