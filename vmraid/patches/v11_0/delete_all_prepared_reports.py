from __future__ import unicode_literals
import vmraid

def execute():
	if vmraid.db.table_exists('Prepared Report'):
		vmraid.reload_doc("core", "doctype", "prepared_report")
		prepared_reports = vmraid.get_all("Prepared Report")
		for report in prepared_reports:
			vmraid.delete_doc("Prepared Report", report.name)
