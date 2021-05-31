# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.utils import validate_email_address

def execute():
	''' update/delete the email group member with the wrong email '''

	email_group_members = vmraid.get_all("Email Group Member", fields=["name", "email"])
	for member in email_group_members:
		validated_email = validate_email_address(member.email)
		if (validated_email==member.email):
			pass
		else:
			try:
				vmraid.db.set_value("Email Group Member", member.name, "email", validated_email)
			except Exception:
				vmraid.delete_doc(doctype="Email Group Member", name=member.name, force=1, ignore_permissions=True)