import vmraid
from vmraid.model.utils.rename_field import rename_field

def execute():
	if not vmraid.db.table_exists('Dashboard Chart'):
		return

	vmraid.reload_doc('desk', 'doctype', 'dashboard_chart')

	if vmraid.db.has_column('Dashboard Chart', 'is_custom'):
		rename_field('Dashboard Chart', 'is_custom', 'use_report_chart')