# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import vmraid


def execute():
	vmraid.reload_doc("core", "doctype", "system_settings", force=1)
	vmraid.db.set_value('System Settings', None, "password_reset_limit", 3)
