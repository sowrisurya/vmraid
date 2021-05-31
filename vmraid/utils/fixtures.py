# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import os

import vmraid
from vmraid.core.doctype.data_import.data_import import export_json, import_doc


def sync_fixtures(app=None):
	"""Import, overwrite fixtures from `[app]/fixtures`"""
	if app:
		apps = [app]
	else:
		apps = vmraid.get_installed_apps()

	vmraid.flags.in_fixtures = True

	for app in apps:
		if os.path.exists(vmraid.get_app_path(app, "fixtures")):
			fixture_files = sorted(os.listdir(vmraid.get_app_path(app, "fixtures")))
			for fname in fixture_files:
				if fname.endswith(".json") or fname.endswith(".csv"):
					import_doc(vmraid.get_app_path(app, "fixtures", fname))

		import_custom_scripts(app)

	vmraid.flags.in_fixtures = False

	vmraid.db.commit()


def import_custom_scripts(app):
	"""Import custom scripts from `[app]/fixtures/custom_scripts`"""
	if os.path.exists(vmraid.get_app_path(app, "fixtures", "custom_scripts")):
		for fname in os.listdir(vmraid.get_app_path(app, "fixtures", "custom_scripts")):
			if fname.endswith(".js"):
				with open(vmraid.get_app_path(app, "fixtures",
					"custom_scripts") + os.path.sep + fname) as f:
					doctype = fname.rsplit(".", 1)[0]
					script = f.read()
					if vmraid.db.exists("Client Script", {"dt": doctype}):
						custom_script = vmraid.get_doc("Client Script", {"dt": doctype})
						custom_script.script = script
						custom_script.save()
					else:
						vmraid.get_doc({
							"doctype": "Client Script",
							"dt": doctype,
							"script": script
						}).insert()


def export_fixtures(app=None):
	"""Export fixtures as JSON to `[app]/fixtures`"""
	if app:
		apps = [app]
	else:
		apps = vmraid.get_installed_apps()
	for app in apps:
		for fixture in vmraid.get_hooks("fixtures", app_name=app):
			filters = None
			or_filters = None
			if isinstance(fixture, dict):
				filters = fixture.get("filters")
				or_filters = fixture.get("or_filters")
				fixture = fixture.get("doctype") or fixture.get("dt")
			print("Exporting {0} app {1} filters {2}".format(fixture, app, (filters if filters else or_filters)))
			if not os.path.exists(vmraid.get_app_path(app, "fixtures")):
				os.mkdir(vmraid.get_app_path(app, "fixtures"))

			export_json(fixture, vmraid.get_app_path(app, "fixtures", vmraid.scrub(fixture) + ".json"),
				filters=filters, or_filters=or_filters, order_by="idx asc, creation asc")
