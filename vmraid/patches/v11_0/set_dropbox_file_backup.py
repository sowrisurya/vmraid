from __future__ import unicode_literals
from vmraid.utils import cint
import vmraid

def execute():
	vmraid.reload_doctype("Dropbox Settings")
	check_dropbox_enabled = cint(vmraid.db.get_value("Dropbox Settings", None, "enabled"))
	if  check_dropbox_enabled == 1:
		vmraid.db.set_value("Dropbox Settings", None, 'file_backup', 1)
