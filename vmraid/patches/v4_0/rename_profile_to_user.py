from __future__ import unicode_literals
import vmraid

from vmraid.model.utils.rename_field import rename_field
from vmraid.model.meta import get_table_columns

def execute():
	tables = vmraid.db.sql_list("show tables")
	if "tabUser" not in tables:
		vmraid.rename_doc("DocType", "Profile", "User", force=True)

	vmraid.reload_doc("website", "doctype", "blogger")

	if "profile" in get_table_columns("Blogger"):
		rename_field("Blogger", "profile", "user")
