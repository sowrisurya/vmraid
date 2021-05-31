from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doctype("User")
	vmraid.db.sql("update `tabUser` set last_active=last_login")
