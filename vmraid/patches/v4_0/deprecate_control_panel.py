# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.db.sql("update `tabDefaultValue` set parenttype='__default' where parenttype='Control Panel'")
	vmraid.db.sql("update `tabDefaultValue` set parent='__default' where parent='Control Panel'")
	vmraid.clear_cache()
