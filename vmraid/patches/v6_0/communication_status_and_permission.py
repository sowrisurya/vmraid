from __future__ import unicode_literals
import vmraid
from vmraid.permissions import reset_perms

def execute():
	vmraid.reload_doctype("Communication")

	# set status = "Linked"
	vmraid.db.sql("""update `tabCommunication` set status='Linked'
		where ifnull(reference_doctype, '')!='' and ifnull(reference_name, '')!=''""")

	vmraid.db.sql("""update `tabCommunication` set status='Closed'
		where status='Archived'""")

	# reset permissions if owner of all DocPerms is Administrator
	if not vmraid.db.sql("""select name from `tabDocPerm`
		where parent='Communication' and ifnull(owner, '')!='Administrator'"""):

		reset_perms("Communication")
