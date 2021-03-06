# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.utils.momentjs import data as momentjs_data

def execute():
	vmraid.reload_doc("core", "doctype", "user")

	ss = vmraid.get_doc("System Settings", "System Settings")
	if ss.time_zone in momentjs_data.get("links"):
		ss.time_zone = momentjs_data["links"][ss.time_zone]
		ss.flags.ignore_mandatory = True
		ss.save()

	for user, time_zone in vmraid.db.sql("select name, time_zone from `tabUser` where ifnull(time_zone, '')!=''"):
		if time_zone in momentjs_data.get("links"):
			user = vmraid.get_doc("User", user)
			user.time_zone = momentjs_data["links"][user.time_zone]
			user.save()
