import vmraid

def execute():
	# convert all /path to path
	vmraid.db.sql('''
		UPDATE `tabWebsite Meta Tag`
		SET parent = SUBSTR(parent, 2)
		WHERE parent like '/%'
	''')
