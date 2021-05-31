from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc("core", "doctype", "user_email")
	vmraid.reload_doc("core", "doctype", "user")
	for user_name in vmraid.get_all('User', filters={'user_type': 'Website User'}):
		user = vmraid.get_doc('User', user_name)
		if user.roles:
			user.roles = []
			user.save()
