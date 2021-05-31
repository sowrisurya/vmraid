import vmraid

def execute():
	vmraid.db.sql('''UPDATE `tabUser Permission`
		SET `modified`=NOW(), `creation`=NOW()
		WHERE `creation` IS NULL''')