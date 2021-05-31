# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	for name in vmraid.db.sql_list("select name from `tabUser` where ifnull(user_image, '')=''"):
		user = vmraid.get_doc("User", name)
		user.update_gravatar()
		user.db_set("user_image", user.user_image)
