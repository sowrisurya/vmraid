from __future__ import unicode_literals
from vmraid.utils import cint
import vmraid

def execute():
	vmraid.reload_doctype('System Settings')
	backup_limit = vmraid.db.get_single_value('System Settings', 'backup_limit')

	if cint(backup_limit) == 0:
		vmraid.db.set_value('System Settings', 'System Settings', 'backup_limit', 3)
