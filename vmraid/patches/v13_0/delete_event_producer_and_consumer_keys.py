# Copyright (c) 2020, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	if vmraid.db.exists("DocType", "Event Producer"):
		vmraid.db.sql("""UPDATE `tabEvent Producer` SET api_key='', api_secret=''""")
	if vmraid.db.exists("DocType", "Event Consumer"):
		vmraid.db.sql("""UPDATE `tabEvent Consumer` SET api_key='', api_secret=''""")
