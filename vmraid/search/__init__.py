# Copyright (c) 2020, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import vmraid
from vmraid.utils import cint
from vmraid.search.website_search import WebsiteSearch
from vmraid.search.full_text_search import FullTextSearch

@vmraid.whitelist(allow_guest=True)
def web_search(query, scope=None, limit=20):
	limit = cint(limit)
	ws = WebsiteSearch(index_name="web_routes")
	return ws.search(query, scope, limit)