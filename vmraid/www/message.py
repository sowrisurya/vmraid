# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

from vmraid.utils import strip_html_tags

no_cache = 1

def get_context(context):
	message_context = {}
	if hasattr(vmraid.local, "message"):
		message_context["header"] = vmraid.local.message_title
		message_context["title"] = strip_html_tags(vmraid.local.message_title)
		message_context["message"] = vmraid.local.message
		if hasattr(vmraid.local, "message_success"):
			message_context["success"] = vmraid.local.message_success

	elif vmraid.local.form_dict.id:
		message_id = vmraid.local.form_dict.id
		key = "message_id:{0}".format(message_id)
		message = vmraid.cache().get_value(key, expires=True)
		if message:
			message_context.update(message.get('context', {}))
			if message.get('http_status_code'):
				vmraid.local.response['http_status_code'] = message['http_status_code']

	return message_context
