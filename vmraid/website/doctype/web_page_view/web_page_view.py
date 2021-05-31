# -*- coding: utf-8 -*-
# Copyright (c) 2020, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.model.document import Document

class WebPageView(Document):
	pass


@vmraid.whitelist(allow_guest=True)
def make_view_log(path, referrer=None, browser=None, version=None, url=None, user_tz=None):
	if not is_tracking_enabled():
		return

	request_dict = vmraid.request.__dict__
	user_agent = request_dict.get('environ', {}).get('HTTP_USER_AGENT')

	if referrer:
		referrer = referrer.split('?')[0]

	is_unique = True
	if referrer.startswith(url):
		is_unique = False

	if path != "/" and path.startswith('/'):
		path = path[1:]

	view = vmraid.new_doc("Web Page View")
	view.path = path
	view.referrer = referrer
	view.browser = browser
	view.browser_version = version
	view.time_zone = user_tz
	view.user_agent = user_agent
	view.is_unique = is_unique

	try:
		view.insert(ignore_permissions=True)
	except Exception:
		if vmraid.message_log:
			vmraid.message_log.pop()

@vmraid.whitelist()
def get_page_view_count(path):
	return vmraid.db.count("Web Page View", filters={'path': path})

def is_tracking_enabled():
	return vmraid.db.get_value("Website Settings", "Website Settings", "enable_view_tracking")