import vmraid

def execute():
	vmraid.reload_doc('core', 'doctype', 'user')
	vmraid.db.sql('''
		UPDATE `tabUser`
		SET `home_settings` = ''
		WHERE `user_type` = 'System User'
	''')
