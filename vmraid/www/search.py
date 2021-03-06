from __future__ import unicode_literals
import vmraid
from vmraid.utils.global_search import web_search
from html2text import html2text
from vmraid import _
from jinja2 import utils
from vmraid.utils import sanitize_html

def get_context(context):
	context.no_cache = 1
	if vmraid.form_dict.q:
		query = str(utils.escape(sanitize_html(vmraid.form_dict.q)))
		context.title = _('Search Results for ')
		context.query = query
		context.route = '/search'
		context.update(get_search_results(query, vmraid.utils.sanitize_html(vmraid.form_dict.scope)))
	else:
		context.title = _('Search')

@vmraid.whitelist(allow_guest = True)
def get_search_results(text, scope=None, start=0, as_html=False):
	results = web_search(text, scope, start, limit=21)
	out = vmraid._dict()

	if len(results) == 21:
		out.has_more = 1
		results = results[:20]

	for d in results:
		try:
			d.content = html2text(d.content)
			index = d.content.lower().index(text.lower())
			d.content = d.content[:index] + '<mark>' + d.content[index:][:len(text)] + '</mark>' + d.content[index + len(text):]

			if index < 40:
				start = 0
				prefix = ''
			else:
				start = index - 40
				prefix = '...'

			suffix = ''
			if (index + len(text) + 47) < len(d.content):
				suffix = '...'

			d.preview = prefix + d.content[start:start + len(text) + 87] + suffix
		except Exception:
			d.preview = html2text(d.content)[:97] + '...'

	out.results = results

	if as_html:
		out.results = vmraid.render_template('templates/includes/search_result.html', out)

	return out
