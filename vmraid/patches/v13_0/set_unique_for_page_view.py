import vmraid

def execute():
	vmraid.reload_doc('website', 'doctype', 'web_page_view', force=True)
	site_url = vmraid.utils.get_site_url(vmraid.local.site)
	vmraid.db.sql("""UPDATE `tabWeb Page View` set is_unique=1 where referrer LIKE '%{0}%'""".format(site_url))
