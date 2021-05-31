from __future__ import unicode_literals

import json
import vmraid
from vmraid.config import get_modules_from_all_apps_for_user
from vmraid.desk.moduleview import get_onboard_items

def execute():
	"""Reset the initial customizations for desk, with modules, indices and links."""
	vmraid.reload_doc("core", "doctype", "user")
	vmraid.db.sql("""update tabUser set home_settings = ''""")
