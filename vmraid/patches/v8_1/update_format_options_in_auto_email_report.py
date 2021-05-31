# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	""" change the XLS option as XLSX in the auto email report """

	vmraid.reload_doc("email", "doctype", "auto_email_report")

	auto_email_list = vmraid.get_all("Auto Email Report", filters={"format": "XLS"})
	for auto_email in auto_email_list:
		vmraid.db.set_value("Auto Email Report", auto_email.name, "format", "XLSX")
