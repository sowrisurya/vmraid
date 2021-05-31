from __future__ import unicode_literals
import vmraid
from vmraid.utils import cint

def execute():
	vmraid.reload_doc("integrations", "doctype", "ldap_settings")

	if not vmraid.db.exists("DocType", "Integration Service"):
		return

	if not vmraid.db.exists("Integration Service", "LDAP"):
		return

	if not cint(vmraid.db.get_value("Integration Service", "LDAP", 'enabled')):
		return

	import ldap
	try:
		ldap_settings = vmraid.get_doc("LDAP Settings")
		ldap_settings.save(ignore_permissions=True)
	except ldap.LDAPError:
		pass
