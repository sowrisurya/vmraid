# -*- coding: utf-8 -*-
# Copyright (c) 2020, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import vmraid
from vmraid.model.document import Document
import vmraid
import json

class DashboardSettings(Document):
	pass


@vmraid.whitelist()
def create_dashboard_settings(user):
	if not vmraid.db.exists("Dashboard Settings", user):
		doc = vmraid.new_doc('Dashboard Settings')
		doc.name = user
		doc.insert(ignore_permissions=True)
		vmraid.db.commit()
		return doc

def get_permission_query_conditions(user):
	if not user: user = vmraid.session.user

	return '''(`tabDashboard Settings`.name = '{user}')'''.format(user=user)

@vmraid.whitelist()
def save_chart_config(reset, config, chart_name):
	reset = vmraid.parse_json(reset)
	doc = vmraid.get_doc('Dashboard Settings', vmraid.session.user)
	chart_config = vmraid.parse_json(doc.chart_config) or {}

	if reset:
		chart_config[chart_name] = {}
	else:
		config = vmraid.parse_json(config)
		if not chart_name in chart_config:
			chart_config[chart_name] = {}
		chart_config[chart_name].update(config)

	vmraid.db.set_value('Dashboard Settings', vmraid.session.user, 'chart_config', json.dumps(chart_config))