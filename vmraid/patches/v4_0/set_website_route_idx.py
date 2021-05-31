from __future__ import unicode_literals
import vmraid

def execute():
	pass
	# from vmraid.website.doctype.website_template.website_template import \
	# 	get_pages_and_generators, get_template_controller
	#
	# vmraid.reload_doc("website", "doctype", "website_template")
	# vmraid.reload_doc("website", "doctype", "website_route")
	#
	# for app in vmraid.get_installed_apps():
	# 	pages, generators = get_pages_and_generators(app)
	# 	for g in generators:
	# 		doctype = vmraid.get_attr(get_template_controller(app, g["path"], g["fname"]) + ".doctype")
	# 		module = vmraid.db.get_value("DocType", doctype, "module")
	# 		vmraid.reload_doc(vmraid.scrub(module), "doctype", vmraid.scrub(doctype))
	#
	# vmraid.db.sql("""update `tabBlog Category` set `title`=`name` where ifnull(`title`, '')=''""")
	# vmraid.db.sql("""update `tabWebsite Route` set idx=null""")
	# for doctype in ["Blog Category", "Blog Post", "Web Page", "Website Group"]:
	# 	vmraid.db.sql("""update `tab{}` set idx=null""".format(doctype))
	#
	# from vmraid.website.doctype.website_template.website_template import rebuild_website_template
	# rebuild_website_template()
