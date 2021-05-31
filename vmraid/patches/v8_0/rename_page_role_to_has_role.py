# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	if not vmraid.db.exists('DocType', 'Has Role'):
		vmraid.rename_doc('DocType', 'Page Role', 'Has Role')
	reload_doc()
	set_ref_doctype_roles_to_report()
	copy_user_roles_to_has_roles()
	remove_doctypes()

def reload_doc():
	vmraid.reload_doc("core", 'doctype', "page")
	vmraid.reload_doc("core", 'doctype', "report")
	vmraid.reload_doc("core", 'doctype', "user")
	vmraid.reload_doc("core", 'doctype', "has_role")
	
def set_ref_doctype_roles_to_report():
	for data in vmraid.get_all('Report', fields=["name"]):
		doc = vmraid.get_doc('Report', data.name)
		if vmraid.db.exists("DocType", doc.ref_doctype):
			try:
				doc.set_doctype_roles()
				for row in doc.roles:
					row.db_update()
			except:
				pass

def copy_user_roles_to_has_roles():
	if vmraid.db.exists('DocType', 'UserRole'):
		for data in vmraid.get_all('User', fields = ["name"]):
			doc = vmraid.get_doc('User', data.name)
			doc.set('roles',[])
			for args in vmraid.get_all('UserRole', fields = ["role"],
				filters = {'parent': data.name, 'parenttype': 'User'}):
				doc.append('roles', {
					'role': args.role
				})
			for role in doc.roles:
				role.db_update()

def remove_doctypes():
	for doctype in ['UserRole', 'Event Role']:
		if vmraid.db.exists('DocType', doctype):
			vmraid.delete_doc('DocType', doctype)