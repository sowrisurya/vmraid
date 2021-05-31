from __future__ import unicode_literals
import vmraid

from vmraid.model.utils.rename_field import rename_field

def execute():
	tables = vmraid.db.sql_list("show tables")
	for doctype in ("Website Sitemap", "Website Sitemap Config"):
		if "tab{}".format(doctype) in tables:
			vmraid.delete_doc("DocType", doctype, force=1)
			vmraid.db.sql("drop table `tab{}`".format(doctype))

	for d in ("Blog Category", "Blog Post", "Web Page"):
		vmraid.reload_doc("website", "doctype", vmraid.scrub(d))
		rename_field_if_exists(d, "parent_website_sitemap", "parent_website_route")

	for d in ("blog_category", "blog_post", "web_page", "post", "user_vote"):
		vmraid.reload_doc("website", "doctype", d)

def rename_field_if_exists(doctype, old_fieldname, new_fieldname):
	try:
		rename_field(doctype, old_fieldname, new_fieldname)
	except vmraid.db.ProgrammingError as e:
		if not vmraid.db.is_column_missing(e):
			raise
