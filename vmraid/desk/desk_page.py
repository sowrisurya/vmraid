# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.translate import send_translations

@vmraid.whitelist()
def get(name):
	"""
	   Return the :term:`doclist` of the `Page` specified by `name`
	"""
	page = vmraid.get_doc('Page', name)
	if page.is_permitted():
		page.load_assets()
		docs = vmraid._dict(page.as_dict())
		if getattr(page, '_dynamic_page', None):
			docs['_dynamic_page'] = 1

		return docs
	else:
		vmraid.response['403'] = 1
		raise vmraid.PermissionError('No read permission for Page %s' %(page.title or name))


@vmraid.whitelist(allow_guest=True)
def getpage():
	"""
	   Load the page from `vmraid.form` and send it via `vmraid.response`
	"""
	page = vmraid.form_dict.get('name')
	doc = get(page)

	# load translations
	if vmraid.lang != "en":
		send_translations(vmraid.get_lang_dict("page", page))

	vmraid.response.docs.append(doc)

def has_permission(page):
	if vmraid.session.user == "Administrator" or "System Manager" in vmraid.get_roles():
		return True

	page_roles = [d.role for d in page.get("roles")]
	if page_roles:
		if vmraid.session.user == "Guest" and "Guest" not in page_roles:
			return False
		elif not set(page_roles).intersection(set(vmraid.get_roles())):
			# check if roles match
			return False

	if not vmraid.has_permission("Page", ptype="read", doc=page):
		# check if there are any user_permissions
		return False
	else:
		# hack for home pages! if no Has Roles, allow everyone to see!
		return True
