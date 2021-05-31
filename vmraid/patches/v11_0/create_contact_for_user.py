from __future__ import unicode_literals
import vmraid
from vmraid.core.doctype.user.user import create_contact
import re

def execute():
	""" Create Contact for each User if not present """
	vmraid.reload_doc('integrations', 'doctype', 'google_contacts')
	vmraid.reload_doc('contacts', 'doctype', 'contact')
	vmraid.reload_doc('core', 'doctype', 'dynamic_link')
	vmraid.reload_doc('communication', 'doctype', 'call_log')

	contact_meta = vmraid.get_meta("Contact")
	if contact_meta.has_field("phone_nos") and contact_meta.has_field("email_ids"):
		vmraid.reload_doc('contacts', 'doctype', 'contact_phone')
		vmraid.reload_doc('contacts', 'doctype', 'contact_email')

	users = vmraid.get_all('User', filters={"name": ('not in', 'Administrator, Guest')}, fields=["*"])
	for user in users:
		if vmraid.db.exists("Contact", {"email_id": user.email}) or vmraid.db.exists("Contact Email", {"email_id": user.email}):
			continue
		if user.first_name:
			user.first_name = re.sub("[<>]+", '', vmraid.safe_decode(user.first_name))
		if user.last_name:
			user.last_name  = re.sub("[<>]+", '', vmraid.safe_decode(user.last_name))
		create_contact(user, ignore_links=True, ignore_mandatory=True)
