# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.utils.scheduler import disable_scheduler, enable_scheduler
from vmraid.utils import cint

def execute():
	vmraid.reload_doc("core", "doctype", "system_settings")
	if cint(vmraid.db.get_global("disable_scheduler")):
		disable_scheduler()
	else:
		enable_scheduler()
