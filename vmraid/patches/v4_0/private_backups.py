# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.installer import make_site_dirs

def execute():
	make_site_dirs()
	if vmraid.local.conf.backup_path and vmraid.local.conf.backup_path.startswith("public"):
		raise Exception("Backups path in conf set to public directory")
