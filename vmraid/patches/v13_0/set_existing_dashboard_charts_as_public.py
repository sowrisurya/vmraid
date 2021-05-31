import vmraid

def execute():
	vmraid.reload_doc('desk', 'doctype', 'dashboard_chart')

	if not vmraid.db.table_exists('Dashboard Chart'):
		return

	users_with_permission = vmraid.get_all(
		"Has Role",
		fields=["parent"],
		filters={"role": ['in', ['System Manager', 'Dashboard Manager']], "parenttype": "User"},
		distinct=True,
	)

	users = [item.parent for item in users_with_permission]
	charts = vmraid.db.get_all('Dashboard Chart', filters={'owner': ['in', users]})

	for chart in charts:
		vmraid.db.set_value('Dashboard Chart', chart.name, 'is_public', 1)

