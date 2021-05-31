# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid
from vmraid import _
import vmraid.sessions
from vmraid.utils import cstr
import os, mimetypes, json
import re

import six
from six import iteritems
from werkzeug.wrappers import Response
from werkzeug.routing import Rule
from werkzeug.wsgi import wrap_file

from vmraid.website.context import get_context
from vmraid.website.redirect import resolve_redirect
from vmraid.website.utils import (get_home_page, can_cache, delete_page_cache,
	get_toc, get_next_link)
from vmraid.website.router import clear_sitemap, evaluate_dynamic_routes
from vmraid.translate import guess_language

class PageNotFoundError(Exception): pass

def render(path=None, http_status_code=None):
	"""render html page"""
	if not path:
		path = vmraid.local.request.path

	try:
		path = path.strip('/ ')
		raise_if_disabled(path)
		resolve_redirect(path)
		path = resolve_path(path)
		data = None

		# if in list of already known 404s, send it
		if can_cache() and vmraid.cache().hget('website_404', vmraid.request.url):
			data = render_page('404')
			http_status_code = 404
		elif is_static_file(path):
			return get_static_file_response()
		elif is_web_form(path):
			data = render_web_form(path)
		else:
			try:
				data = render_page_by_language(path)
			except vmraid.PageDoesNotExistError:
				doctype, name = get_doctype_from_path(path)
				if doctype and name:
					path = "printview"
					vmraid.local.form_dict.doctype = doctype
					vmraid.local.form_dict.name = name
				elif doctype:
					path = "list"
					vmraid.local.form_dict.doctype = doctype
				else:
					# 404s are expensive, cache them!
					vmraid.cache().hset('website_404', vmraid.request.url, True)
					data = render_page('404')
					http_status_code = 404

				if not data:
					try:
						data = render_page(path)
					except vmraid.PermissionError as e:
						data, http_status_code = render_403(e, path)

			except vmraid.PermissionError as e:
				data, http_status_code = render_403(e, path)

			except vmraid.Redirect as e:
				raise e

			except Exception:
				path = "error"
				data = render_page(path)
				http_status_code = 500

		data = add_csrf_token(data)

	except vmraid.Redirect:
		return build_response(path, "", 301, {
			"Location": vmraid.flags.redirect_location or (vmraid.local.response or {}).get('location'),
			"Cache-Control": "no-store, no-cache, must-revalidate"
		})

	return build_response(path, data, http_status_code or 200)

def is_static_file(path):
	if ('.' not in path):
		return False
	extn = path.rsplit('.', 1)[-1]
	if extn in ('html', 'md', 'js', 'xml', 'css', 'txt', 'py', 'json'):
		return False

	for app in vmraid.get_installed_apps():
		file_path = vmraid.get_app_path(app, 'www') + '/' + path
		if os.path.exists(file_path):
			vmraid.flags.file_path = file_path
			return True

	return False

def is_web_form(path):
	return bool(vmraid.get_all("Web Form", filters={'route': path}))

def render_web_form(path):
	data = render_page(path)
	return data

def get_static_file_response():
	try:
		f = open(vmraid.flags.file_path, 'rb')
	except IOError:
		raise NotFound

	response = Response(wrap_file(vmraid.local.request.environ, f), direct_passthrough=True)
	response.mimetype = mimetypes.guess_type(vmraid.flags.file_path)[0] or 'application/octet-stream'
	return response

def build_response(path, data, http_status_code, headers=None):
	# build response
	response = Response()
	response.data = set_content_type(response, data, path)
	response.status_code = http_status_code
	response.headers["X-Page-Name"] = path.encode("ascii", errors="xmlcharrefreplace")
	response.headers["X-From-Cache"] = vmraid.local.response.from_cache or False

	add_preload_headers(response)
	if headers:
		for key, val in iteritems(headers):
			response.headers[key] = val.encode("ascii", errors="xmlcharrefreplace")

	return response


def add_preload_headers(response):
	from bs4 import BeautifulSoup

	try:
		preload = []
		soup = BeautifulSoup(response.data, "lxml")
		for elem in soup.find_all('script', src=re.compile(".*")):
			preload.append(("script", elem.get("src")))

		for elem in soup.find_all('link', rel="stylesheet"):
			preload.append(("style", elem.get("href")))

		links = []
		for _type, link in preload:
			links.append("<{}>; rel=preload; as={}".format(link, _type))

		if links:
			response.headers["Link"] = ",".join(links)
	except Exception:
		import traceback
		traceback.print_exc()


def render_page_by_language(path):
	translated_languages = vmraid.get_hooks("translated_languages_for_website")
	user_lang = guess_language(translated_languages)
	if translated_languages and user_lang in translated_languages:
		try:
			if path and path != "index":
				lang_path = '{0}/{1}'.format(user_lang, path)
			else:
				lang_path = user_lang # index

			return render_page(lang_path)
		except vmraid.DoesNotExistError:
			return render_page(path)

	else:
		return render_page(path)

def render_page(path):
	"""get page html"""
	out = None

	if can_cache():
		# return rendered page
		page_cache = vmraid.cache().hget("website_page", path)
		if page_cache and vmraid.local.lang in page_cache:
			out = page_cache[vmraid.local.lang]

	if out:
		vmraid.local.response.from_cache = True
		return out

	return build(path)

def build(path):
	if not vmraid.db:
		vmraid.connect()

	try:
		return build_page(path)
	except vmraid.DoesNotExistError:
		hooks = vmraid.get_hooks()
		if hooks.website_catch_all:
			path = hooks.website_catch_all[0]
			return build_page(path)
		else:
			raise
	except Exception:
		raise

def build_page(path):
	if not getattr(vmraid.local, "path", None):
		vmraid.local.path = path

	context = get_context(path)

	if context.source:
		html = vmraid.render_template(context.source, context)
	elif context.template:
		if path.endswith('min.js'):
			html = vmraid.get_jloader().get_source(vmraid.get_jenv(), context.template)[0]
		else:
			html = vmraid.get_template(context.template).render(context)

	if '{index}' in html:
		html = html.replace('{index}', get_toc(context.route))

	if '{next}' in html:
		html = html.replace('{next}', get_next_link(context.route))

	# html = vmraid.get_template(context.base_template_path).render(context)

	if can_cache(context.no_cache):
		page_cache = vmraid.cache().hget("website_page", path) or {}
		page_cache[vmraid.local.lang] = html
		vmraid.cache().hset("website_page", path, page_cache)

	return html

def resolve_path(path):
	if not path:
		path = "index"

	if path.endswith('.html'):
		path = path[:-5]

	if path == "index":
		path = get_home_page()

	vmraid.local.path = path

	if path != "index":
		path = resolve_from_map(path)

	return path

def resolve_from_map(path):
	'''transform dynamic route to a static one from hooks and route defined in doctype'''
	rules = [Rule(r["from_route"], endpoint=r["to_route"], defaults=r.get("defaults"))
		for r in get_website_rules()]

	return evaluate_dynamic_routes(rules, path) or path

def get_website_rules():
	'''Get website route rules from hooks and DocType route'''
	def _get():
		rules = vmraid.get_hooks("website_route_rules")
		for d in vmraid.get_all('DocType', 'name, route', dict(has_web_view=1)):
			if d.route:
				rules.append(dict(from_route = '/' + d.route.strip('/'), to_route=d.name))

		return rules

	if vmraid.local.dev_server:
		# dont cache in development
		return _get()

	return vmraid.cache().get_value('website_route_rules', _get)

def set_content_type(response, data, path):
	if isinstance(data, dict):
		response.mimetype = 'application/json'
		response.charset = 'utf-8'
		data = json.dumps(data)
		return data

	response.mimetype = 'text/html'
	response.charset = 'utf-8'

	if "." in path:
		content_type, encoding = mimetypes.guess_type(path)
		if content_type:
			response.mimetype = content_type
			if encoding:
				response.charset = encoding

	return data

def clear_cache(path=None):
	'''Clear website caches

	:param path: (optional) for the given path'''
	for key in ('website_generator_routes', 'website_pages',
		'website_full_index', 'sitemap_routes'):
		vmraid.cache().delete_value(key)

	vmraid.cache().delete_value("website_404")
	if path:
		vmraid.cache().hdel('website_redirects', path)
		delete_page_cache(path)
	else:
		clear_sitemap()
		vmraid.clear_cache("Guest")
		for key in ('portal_menu_items', 'home_page', 'website_route_rules',
			'doctypes_with_web_view', 'website_redirects', 'page_context',
			'website_page'):
			vmraid.cache().delete_value(key)

	for method in vmraid.get_hooks("website_clear_cache"):
		vmraid.get_attr(method)(path)

def render_403(e, pathname):
	vmraid.local.message = cstr(e.message if six.PY2 else e)
	vmraid.local.message_title = _("Not Permitted")
	vmraid.local.response['context'] = dict(
		indicator_color = 'red',
		primary_action = '/login',
		primary_label = _('Login'),
		fullpage=True
	)
	return render_page("message"), e.http_status_code

def get_doctype_from_path(path):
	doctypes = vmraid.db.sql_list("select name from tabDocType")

	parts = path.split("/")

	doctype = parts[0]
	name = parts[1] if len(parts) > 1 else None

	if doctype in doctypes:
		return doctype, name

	# try scrubbed
	doctype = doctype.replace("_", " ").title()
	if doctype in doctypes:
		return doctype, name

	return None, None

def add_csrf_token(data):
	if vmraid.local.session:
		return data.replace("<!-- csrf_token -->", '<script>vmraid.csrf_token = "{0}";</script>'.format(
				vmraid.local.session.data.csrf_token))
	else:
		return data

def raise_if_disabled(path):
	routes = vmraid.db.get_all('Portal Menu Item',
		fields=['route', 'enabled'],
		filters={
			'enabled': 0,
			'route': ['like', '%{0}'.format(path)]
		}
	)

	for r in routes:
		_path = r.route.lstrip('/')
		if path == _path and not r.enabled:
			raise vmraid.PermissionError
