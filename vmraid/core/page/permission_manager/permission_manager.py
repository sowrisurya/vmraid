# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid
from vmraid import _
import vmraid.defaults
from vmraid.modules.import_file import get_file_path, read_doc_from_file
from vmraid.translate import send_translations
from vmraid.core.doctype.doctype.doctype import (clear_permissions_cache,
	validate_permissions_for_doctype)
from vmraid.permissions import (reset_perms, get_linked_doctypes, get_all_perms,
	setup_custom_perms, add_permission, update_permission_property)
from vmraid.utils.user import get_users_with_role as _get_user_with_role

not_allowed_in_permission_manager = ["DocType", "Patch Log", "Module Def", "Transaction Log"]

@vmraid.whitelist()
def get_roles_and_doctypes():
	vmraid.only_for("System Manager")
	send_translations(vmraid.get_lang_dict("doctype", "DocPerm"))

	active_domains = vmraid.get_active_domains()

	doctypes = vmraid.get_all("DocType", filters={
		"istable": 0,
		"name": ("not in", ",".join(not_allowed_in_permission_manager)),
	}, or_filters={
		"ifnull(restrict_to_domain, '')": "",
		"restrict_to_domain": ("in", active_domains)
	}, fields=["name"])

	restricted_roles = ['Administrator']
	if vmraid.session.user != 'Administrator':
		custom_user_type_roles = vmraid.get_all('User Type', filters = {'is_standard': 0}, fields=['role'])
		for row in custom_user_type_roles:
			restricted_roles.append(row.role)

		restricted_roles.append('All')

	roles = vmraid.get_all("Role", filters={
		"name": ("not in", restricted_roles),
		"disabled": 0,
	}, or_filters={
		"ifnull(restrict_to_domain, '')": "",
		"restrict_to_domain": ("in", active_domains)
	}, fields=["name"])

	doctypes_list = [ {"label":_(d.get("name")), "value":d.get("name")} for d in doctypes]
	roles_list = [ {"label":_(d.get("name")), "value":d.get("name")} for d in roles]

	return {
		"doctypes": sorted(doctypes_list, key=lambda d: d['label']),
		"roles": sorted(roles_list, key=lambda d: d['label'])
	}

@vmraid.whitelist()
def get_permissions(doctype=None, role=None):
	vmraid.only_for("System Manager")
	if role:
		out = get_all_perms(role)
		if doctype:
			out = [p for p in out if p.parent == doctype]
	else:
		filters=dict(parent = doctype)
		if vmraid.session.user != 'Administrator':
			custom_roles = vmraid.get_all('Role', filters={'is_custom': 1})
			filters['role'] = ['not in', [row.name for row in custom_roles]]

		out = vmraid.get_all('Custom DocPerm', fields='*', filters=filters, order_by="permlevel")
		if not out:
			out = vmraid.get_all('DocPerm', fields='*', filters=filters, order_by="permlevel")

	linked_doctypes = {}
	for d in out:
		if not d.parent in linked_doctypes:
			linked_doctypes[d.parent] = get_linked_doctypes(d.parent)
		d.linked_doctypes = linked_doctypes[d.parent]
		meta = vmraid.get_meta(d.parent)
		if meta:
			d.is_submittable = meta.is_submittable
			d.in_create = meta.in_create

	return out

@vmraid.whitelist()
def add(parent, role, permlevel):
	vmraid.only_for("System Manager")
	add_permission(parent, role, permlevel)

@vmraid.whitelist()
def update(doctype, role, permlevel, ptype, value=None):
	"""Update role permission params

	Args:
	    doctype (str): Name of the DocType to update params for
	    role (str): Role to be updated for, eg "Website Manager".
	    permlevel (int): perm level the provided rule applies to
	    ptype (str): permission type, example "read", "delete", etc.
	    value (None, optional): value for ptype, None indicates False

	Returns:
	    str: Refresh flag is permission is updated successfully
	"""
	vmraid.only_for("System Manager")
	out = update_permission_property(doctype, role, permlevel, ptype, value)
	return 'refresh' if out else None

@vmraid.whitelist()
def remove(doctype, role, permlevel):
	vmraid.only_for("System Manager")
	setup_custom_perms(doctype)

	name = vmraid.get_value('Custom DocPerm', dict(parent=doctype, role=role, permlevel=permlevel))

	vmraid.db.sql('delete from `tabCustom DocPerm` where name=%s', name)
	if not vmraid.get_all('Custom DocPerm', dict(parent=doctype)):
		vmraid.throw(_('There must be atleast one permission rule.'), title=_('Cannot Remove'))

	validate_permissions_for_doctype(doctype, for_remove=True, alert=True)

@vmraid.whitelist()
def reset(doctype):
	vmraid.only_for("System Manager")
	reset_perms(doctype)
	clear_permissions_cache(doctype)

@vmraid.whitelist()
def get_users_with_role(role):
	vmraid.only_for("System Manager")
	return _get_user_with_role(role)

@vmraid.whitelist()
def get_standard_permissions(doctype):
	vmraid.only_for("System Manager")
	meta = vmraid.get_meta(doctype)
	if meta.custom:
		doc = vmraid.get_doc('DocType', doctype)
		return [p.as_dict() for p in doc.permissions]
	else:
		# also used to setup permissions via patch
		path = get_file_path(meta.module, "DocType", doctype)
		return read_doc_from_file(path).get("permissions")
