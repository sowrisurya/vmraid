from __future__ import unicode_literals
import vmraid

def execute():
	# clear all static web pages
	vmraid.delete_doc("DocType", "Website Route", force=1)
	vmraid.delete_doc("Page", "sitemap-browser", force=1)
	vmraid.db.sql("drop table if exists `tabWebsite Route`")
