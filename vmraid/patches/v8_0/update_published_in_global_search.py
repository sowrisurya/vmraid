from __future__ import unicode_literals
import vmraid

def execute():
	from vmraid.website.router import get_doctypes_with_web_view
	from vmraid.utils.global_search import rebuild_for_doctype

	for doctype in get_doctypes_with_web_view():
		try:
			rebuild_for_doctype(doctype)
		except vmraid.DoesNotExistError:
			pass
