# Copyright (c) 2021, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid
import json

def execute():
	"""Convert Query Report json to support other content"""
	records = vmraid.get_all('Report',
		filters={
			"json": ["!=", ""]
		},
		fields=["name", "json"]
	)
	for record in records:
		jstr = record["json"]
		data = json.loads(jstr)
		if isinstance(data, list):
			# double escape braces
			jstr = f'{{"columns":{jstr}}}'
			vmraid.db.update('Report', record["name"], "json", jstr)
