# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import vmraid
from vmraid.model.document import get_controller
from vmraid.utils import get_datetime, nowdate, get_url
from vmraid.website.router import get_pages, get_all_page_context_from_doctypes
from six import iteritems
from six.moves.urllib.parse import quote, urljoin

no_cache = 1
base_template_path = "templates/www/sitemap.xml"

def get_context(context):
	"""generate the sitemap XML"""

	# the site might be accessible from multiple host_names
	# for e.g gadgets.erpadda.com and gadgetsinternational.com
	# so it should be picked from the request
	host = vmraid.utils.get_host_name_from_request()

	links = []
	for route, page in iteritems(get_pages()):
		if page.sitemap:
			links.append({
				"loc": get_url(quote(page.name.encode("utf-8"))),
				"lastmod": nowdate()
			})

	for route, data in iteritems(get_public_pages_from_doctypes()):
		links.append({
			"loc": get_url(quote((route or "").encode("utf-8"))),
			"lastmod": get_datetime(data.get("modified")).strftime("%Y-%m-%d")
		})

	return {"links":links}

def get_public_pages_from_doctypes():
	'''Returns pages from doctypes that are publicly accessible'''

	def get_sitemap_routes():
		routes = {}
		doctypes_with_web_view = [d.name for d in vmraid.db.get_all('DocType', {
			'has_web_view': 1,
			'allow_guest_to_view': 1
		})]

		for doctype in doctypes_with_web_view:
			controller = get_controller(doctype)
			meta = vmraid.get_meta(doctype)
			condition_field = meta.is_published_field or controller.website.condition_field

			try:
				res = vmraid.db.get_all(doctype, ['route', 'name', 'modified'], { condition_field: 1 })
				for r in res:
					routes[r.route] = {"doctype": doctype, "name": r.name, "modified": r.modified}

			except Exception as e:
				if not vmraid.db.is_missing_column(e): raise e

		return routes

	return vmraid.cache().get_value("sitemap_routes", get_sitemap_routes)
