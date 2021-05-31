# -*- coding: utf-8 -*-
# Copyright (c) 2017, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import base64
import datetime
import hashlib
import hmac
import json
from time import sleep

import requests
from six.moves.urllib.parse import urlparse

import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.utils.jinja import validate_template
from vmraid.utils.safe_exec import get_safe_globals

WEBHOOK_SECRET_HEADER = "X-VMRaid-Webhook-Signature"


class Webhook(Document):
	def validate(self):
		self.validate_docevent()
		self.validate_condition()
		self.validate_request_url()
		self.validate_request_body()
		self.validate_repeating_fields()

	def on_update(self):
		vmraid.cache().delete_value('webhooks')

	def validate_docevent(self):
		if self.webhook_doctype:
			is_submittable = vmraid.get_value("DocType", self.webhook_doctype, "is_submittable")
			if not is_submittable and self.webhook_docevent in ["on_submit", "on_cancel", "on_update_after_submit"]:
				vmraid.throw(_("DocType must be Submittable for the selected Doc Event"))

	def validate_condition(self):
		temp_doc = vmraid.new_doc(self.webhook_doctype)
		if self.condition:
			try:
				vmraid.safe_eval(self.condition, eval_locals=get_context(temp_doc))
			except Exception as e:
				vmraid.throw(_(e))

	def validate_request_url(self):
		try:
			request_url = urlparse(self.request_url).netloc
			if not request_url:
				raise vmraid.ValidationError
		except Exception as e:
			vmraid.throw(_("Check Request URL"), exc=e)

	def validate_request_body(self):
		if self.request_structure:
			if self.request_structure == "Form URL-Encoded":
				self.webhook_json = None
			elif self.request_structure == "JSON":
				validate_json(self.webhook_json)
				validate_template(self.webhook_json)
				self.webhook_data = []

	def validate_repeating_fields(self):
		"""Error when Same Field is entered multiple times in webhook_data"""
		webhook_data = []
		for entry in self.webhook_data:
			webhook_data.append(entry.fieldname)

		if len(webhook_data) != len(set(webhook_data)):
			vmraid.throw(_("Same Field is entered more than once"))


def get_context(doc):
	return {'doc': doc, 'utils': get_safe_globals().get('vmraid').get('utils')}

def enqueue_webhook(doc, webhook):
	webhook = vmraid.get_doc("Webhook", webhook.get("name"))
	headers = get_webhook_headers(doc, webhook)
	data = get_webhook_data(doc, webhook)

	for i in range(3):
		try:
			r = requests.post(webhook.request_url, data=json.dumps(data, default=str), headers=headers, timeout=5)
			r.raise_for_status()
			vmraid.logger().debug({"webhook_success": r.text})
			break
		except Exception as e:
			vmraid.logger().debug({"webhook_error": e, "try": i + 1})
			sleep(3 * i + 1)
			if i != 2:
				continue
			else:
				raise e


def get_webhook_headers(doc, webhook):
	headers = {}

	if webhook.enable_security:
		data = get_webhook_data(doc, webhook)
		signature = base64.b64encode(
			hmac.new(
				webhook.get_password("webhook_secret").encode("utf8"),
				json.dumps(data).encode("utf8"),
				hashlib.sha256
			).digest()
		)
		headers[WEBHOOK_SECRET_HEADER] = signature

	if webhook.webhook_headers:
		for h in webhook.webhook_headers:
			if h.get("key") and h.get("value"):
				headers[h.get("key")] = h.get("value")

	return headers


def get_webhook_data(doc, webhook):
	data = {}
	doc = doc.as_dict(convert_dates_to_str=True)

	if webhook.webhook_data:
		data = {w.key: doc.get(w.fieldname) for w in webhook.webhook_data}
	elif webhook.webhook_json:
		data = vmraid.render_template(webhook.webhook_json, get_context(doc))
		data = json.loads(data)

	return data


def validate_json(string):
	try:
		json.loads(string)
	except (TypeError, ValueError):
		vmraid.throw(_("Request Body consists of an invalid JSON structure"), title=_("Invalid JSON"))
