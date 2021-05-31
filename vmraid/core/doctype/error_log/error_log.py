# -*- coding: utf-8 -*-
# Copyright (c) 2015, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.model.document import Document

class ErrorLog(Document):
	def onload(self):
		if not self.seen:
			self.db_set('seen', 1, update_modified=0)
			vmraid.db.commit()

def set_old_logs_as_seen():
	# set logs as seen
	vmraid.db.sql("""UPDATE `tabError Log` SET `seen`=1
		WHERE `seen`=0 AND `creation` < (NOW() - INTERVAL '7' DAY)""")

@vmraid.whitelist()
def clear_error_logs():
	'''Flush all Error Logs'''
	vmraid.only_for('System Manager')
	vmraid.db.sql('''DELETE FROM `tabError Log`''')