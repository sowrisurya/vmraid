from __future__ import unicode_literals
import vmraid
from vmraid.model.base_document import get_controller

def execute():
	update_routes(['Blog Post', 'Blog Category', 'Web Page'])

def update_routes(doctypes):
	"""Patch old routing system"""
	for d in doctypes:
		vmraid.reload_doctype(d)
		c = get_controller(d)

		condition = ''
		if c.website.condition_field:
			condition = 'where {0}=1'.format(c.website.condition_field)

		try:
			vmraid.db.sql("""update ignore `tab{0}` set route = concat(ifnull(parent_website_route, ""),
				if(ifnull(parent_website_route, "")="", "", "/"), page_name) {1}""".format(d, condition))

		except Exception as e:
			if not vmraid.db.is_missing_column(e): raise
