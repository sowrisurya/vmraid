from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doctype("Error Log")

	from vmraid.core.doctype.error_log.error_log import set_old_logs_as_seen
	set_old_logs_as_seen()
