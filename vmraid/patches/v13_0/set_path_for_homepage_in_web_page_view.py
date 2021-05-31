import vmraid

def execute():
	vmraid.reload_doc('website', 'doctype', 'web_page_view', force=True)
	vmraid.db.sql("""UPDATE `tabWeb Page View` set path="/" where path=''""")
