# -*- coding: utf-8 -*-
# Copyright (c) 2019, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid, os
from vmraid import _
from vmraid.model.document import Document
from vmraid.modules.export_file import export_to_files
from vmraid.modules import get_module_path, scrub


@vmraid.whitelist()
def get_config(name):
	doc = vmraid.get_doc('Dashboard Chart Source', name)
	with open(os.path.join(get_module_path(doc.module),
		'dashboard_chart_source', scrub(doc.name), scrub(doc.name) + '.js'), 'r') as f:
		return f.read()

class DashboardChartSource(Document):
	def on_update(self):
		export_to_files(record_list=[[self.doctype, self.name]],
			record_module=self.module, create_init=True)
