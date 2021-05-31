from __future__ import unicode_literals
import vmraid, json

def execute():
	vmraid.clear_cache()
	installed = vmraid.get_installed_apps()
	if "webnotes" in installed:
		installed.remove("webnotes")
	if "vmraid" not in installed:
		installed = ["vmraid"] + installed
	vmraid.db.set_global("installed_apps", json.dumps(installed))
	vmraid.clear_cache()
