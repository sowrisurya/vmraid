# -*- coding: utf-8 -*-
# Copyright (c) 2020, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json

import vmraid
from vmraid.utils.safe_exec import safe_exec
from vmraid.model.document import Document

class SystemConsole(Document):
	def run(self):
		vmraid.only_for('System Manager')
		try:
			vmraid.debug_log = []
			safe_exec(self.console)
			self.output = '\n'.join(vmraid.debug_log)
		except: # noqa: E722
			self.output = vmraid.get_traceback()

		if self.commit:
			vmraid.db.commit()
		else:
			vmraid.db.rollback()

		vmraid.get_doc(dict(
			doctype='Console Log',
			script=self.console,
			output=self.output)).insert()
		vmraid.db.commit()

@vmraid.whitelist()
def execute_code(doc):
	console = vmraid.get_doc(json.loads(doc))
	console.run()
	return console.as_dict()