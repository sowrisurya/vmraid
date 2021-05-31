# -*- coding: utf-8 -*-
# Copyright (c) 2017, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import vmraid


def run_webhooks(doc, method):
	'''Run webhooks for this method'''
	if vmraid.flags.in_import or vmraid.flags.in_patch or vmraid.flags.in_install:
		return

	if vmraid.flags.webhooks_executed is None:
		vmraid.flags.webhooks_executed = {}

	if vmraid.flags.webhooks is None:
		# load webhooks from cache
		webhooks = vmraid.cache().get_value('webhooks')
		if webhooks is None:
			# query webhooks
			webhooks_list = vmraid.get_all('Webhook',
						fields=["name", "`condition`", "webhook_docevent", "webhook_doctype"], 
						filters={"enabled": True}
					)

			# make webhooks map for cache
			webhooks = {}
			for w in webhooks_list:
				webhooks.setdefault(w.webhook_doctype, []).append(w)
			vmraid.cache().set_value('webhooks', webhooks)

		vmraid.flags.webhooks = webhooks

	# get webhooks for this doctype
	webhooks_for_doc = vmraid.flags.webhooks.get(doc.doctype, None)

	if not webhooks_for_doc:
		# no webhooks, quit
		return

	def _webhook_request(webhook):
		if webhook.name not in vmraid.flags.webhooks_executed.get(doc.name, []):
			vmraid.enqueue("vmraid.integrations.doctype.webhook.webhook.enqueue_webhook",
				enqueue_after_commit=True, doc=doc, webhook=webhook)

			# keep list of webhooks executed for this doc in this request
			# so that we don't run the same webhook for the same document multiple times
			# in one request
			vmraid.flags.webhooks_executed.setdefault(doc.name, []).append(webhook.name)

	event_list = ["on_update", "after_insert", "on_submit", "on_cancel", "on_trash"]

	if not doc.flags.in_insert:
		# value change is not applicable in insert
		event_list.append('on_change')
		event_list.append('before_update_after_submit')

	from vmraid.integrations.doctype.webhook.webhook import get_context

	for webhook in webhooks_for_doc:
		trigger_webhook = False
		event = method if method in event_list else None
		if not webhook.condition:
			trigger_webhook = True
		elif vmraid.safe_eval(webhook.condition, eval_locals=get_context(doc)):
			trigger_webhook = True

		if trigger_webhook and event and webhook.webhook_docevent == event:
			_webhook_request(webhook)
