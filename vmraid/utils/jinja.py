# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

def get_jenv():
	import vmraid
	from vmraid.utils.safe_exec import get_safe_globals

	if not getattr(vmraid.local, 'jenv', None):
		from jinja2 import DebugUndefined
		from jinja2.sandbox import SandboxedEnvironment

		# vmraid will be loaded last, so app templates will get precedence
		jenv = SandboxedEnvironment(
			loader=get_jloader(),
			undefined=DebugUndefined
		)
		set_filters(jenv)

		jenv.globals.update(get_safe_globals())

		methods, filters = get_jinja_hooks()
		jenv.globals.update(methods or {})
		jenv.filters.update(filters or {})

		vmraid.local.jenv = jenv

	return vmraid.local.jenv

def get_template(path):
	return get_jenv().get_template(path)

def get_email_from_template(name, args):
	from jinja2 import TemplateNotFound

	args = args or {}
	try:
		message = get_template('templates/emails/' + name + '.html').render(args)
	except TemplateNotFound as e:
		raise e

	try:
		text_content = get_template('templates/emails/' + name + '.txt').render(args)
	except TemplateNotFound:
		text_content = None

	return (message, text_content)

def validate_template(html):
	"""Throws exception if there is a syntax error in the Jinja Template"""
	import vmraid
	from jinja2 import TemplateSyntaxError

	jenv = get_jenv()
	try:
		jenv.from_string(html)
	except TemplateSyntaxError as e:
		vmraid.msgprint('Line {}: {}'.format(e.lineno, e.message))
		vmraid.throw(vmraid._("Syntax error in template"))

def render_template(template, context, is_path=None, safe_render=True):
	'''Render a template using Jinja

	:param template: path or HTML containing the jinja template
	:param context: dict of properties to pass to the template
	:param is_path: (optional) assert that the `template` parameter is a path
	:param safe_render: (optional) prevent server side scripting via jinja templating
	'''

	from vmraid import get_traceback, throw
	from jinja2 import TemplateError

	if not template:
		return ""

	if (is_path or guess_is_path(template)):
		return get_jenv().get_template(template).render(context)
	else:
		if safe_render and ".__" in template:
			throw("Illegal template")
		try:
			return get_jenv().from_string(template).render(context)
		except TemplateError:
			throw(title="Jinja Template Error", msg="<pre>{template}</pre><pre>{tb}</pre>".format(template=template, tb=get_traceback()))

def guess_is_path(template):
	# template can be passed as a path or content
	# if its single line and ends with a html, then its probably a path
	if '\n' not in template and '.' in template:
		extn = template.rsplit('.')[-1]
		if extn in ('html', 'css', 'scss', 'py', 'md', 'json', 'js', 'xml'):
			return True

	return False


def get_jloader():
	import vmraid
	if not getattr(vmraid.local, 'jloader', None):
		from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

		if vmraid.local.flags.in_setup_help:
			apps = ['vmraid']
		else:
			apps = vmraid.get_hooks('template_apps')
			if not apps:
				apps = vmraid.local.flags.web_pages_apps or vmraid.get_installed_apps(sort=True)
				apps.reverse()

		if "vmraid" not in apps:
			apps.append('vmraid')

		vmraid.local.jloader = ChoiceLoader(
			# search for something like app/templates/...
			[PrefixLoader(dict(
				(app, PackageLoader(app, ".")) for app in apps
			))]

			# search for something like templates/...
			+ [PackageLoader(app, ".") for app in apps]
		)

	return vmraid.local.jloader

def set_filters(jenv):
	import vmraid
	from vmraid.utils import cint, cstr, flt

	jenv.filters["json"] = vmraid.as_json
	jenv.filters["len"] = len
	jenv.filters["int"] = cint
	jenv.filters["str"] = cstr
	jenv.filters["flt"] = flt

	if vmraid.flags.in_setup_help:
		return


def get_jinja_hooks():
	"""Returns a tuple of (methods, filters) each containing a dict of method name and method definition pair."""
	import vmraid

	if not getattr(vmraid.local, "site", None):
		return (None, None)

	from types import FunctionType, ModuleType
	from inspect import getmembers, isfunction

	def get_obj_dict_from_paths(object_paths):
		out = {}
		for obj_path in object_paths:
			try:
				obj = vmraid.get_module(obj_path)
			except ModuleNotFoundError:
				obj = vmraid.get_attr(obj_path)

			if isinstance(obj, ModuleType):
				functions = getmembers(obj, isfunction)
				for function_name, function in functions:
					out[function_name] = function
			elif isinstance(obj, FunctionType):
				function_name = obj.__name__
				out[function_name] = obj
		return out

	values = vmraid.get_hooks("jinja")
	methods, filters = values.get("methods", []), values.get("filters", [])

	method_dict = get_obj_dict_from_paths(methods)
	filter_dict = get_obj_dict_from_paths(filters)

	return method_dict, filter_dict
