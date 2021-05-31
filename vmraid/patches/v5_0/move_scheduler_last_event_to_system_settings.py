from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doctype('System Settings')
	last = vmraid.db.get_global('scheduler_last_event')
	vmraid.db.set_value('System Settings', 'System Settings', 'scheduler_last_event', last)

