from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc("Core", "DocType", "User")
	
	for user in vmraid.db.get_all('User'):
		user = vmraid.get_doc('User', user.name)
		user.set_full_name()
		user.db_set('full_name', user.full_name, update_modified = False)