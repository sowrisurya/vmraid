
import os, json, inspect
import mimetypes
from html2text import html2text
from RestrictedPython import compile_restricted, safe_globals
import RestrictedPython.Guards
import vmraid
import vmraid.utils
import vmraid.utils.data
from vmraid.website.utils import (get_shade, get_toc, get_next_link)
from vmraid.modules import scrub
from vmraid.www.printview import get_visible_columns
import vmraid.exceptions
import vmraid.integrations.utils
from vmraid.vmraidclient import VMRaidClient

class ServerScriptNotEnabled(vmraid.PermissionError):
	pass

class NamespaceDict(vmraid._dict):
	"""Raise AttributeError if function not found in namespace"""
	def __getattr__(self, key):
		ret = self.get(key)
		if (not ret and key.startswith("__")) or (key not in self):
			def default_function(*args, **kwargs):
				raise AttributeError(f"module has no attribute '{key}'")
			return default_function
		return ret


def safe_exec(script, _globals=None, _locals=None):
	# script reports must be enabled via site_config.json
	if not vmraid.conf.server_script_enabled:
		vmraid.throw('Please Enable Server Scripts', ServerScriptNotEnabled)

	# build globals
	exec_globals = get_safe_globals()
	if _globals:
		exec_globals.update(_globals)

	# execute script compiled by RestrictedPython
	exec(compile_restricted(script), exec_globals, _locals) # pylint: disable=exec-used

	return exec_globals, _locals

def get_safe_globals():
	datautils = vmraid._dict()
	if vmraid.db:
		date_format = vmraid.db.get_default("date_format") or "yyyy-mm-dd"
		time_format = vmraid.db.get_default("time_format") or "HH:mm:ss"
	else:
		date_format = "yyyy-mm-dd"
		time_format = "HH:mm:ss"

	add_data_utils(datautils)

	if "_" in getattr(vmraid.local, 'form_dict', {}):
		del vmraid.local.form_dict["_"]

	user = getattr(vmraid.local, "session", None) and vmraid.local.session.user or "Guest"

	out = NamespaceDict(
		# make available limited methods of vmraid
		json=json,
		dict=dict,
		log=vmraid.log,
		_dict=vmraid._dict,
		vmraid=NamespaceDict(
			flags=vmraid._dict(),
			format=vmraid.format_value,
			format_value=vmraid.format_value,
			date_format=date_format,
			time_format=time_format,
			format_date=vmraid.utils.data.global_date_format,
			form_dict=getattr(vmraid.local, 'form_dict', {}),
			bold=vmraid.bold,
			copy_doc=vmraid.copy_doc,

			get_meta=vmraid.get_meta,
			get_doc=vmraid.get_doc,
			get_cached_doc=vmraid.get_cached_doc,
			get_list=vmraid.get_list,
			get_all=vmraid.get_all,
			get_system_settings=vmraid.get_system_settings,

			utils=datautils,
			get_url=vmraid.utils.get_url,
			render_template=vmraid.render_template,
			msgprint=vmraid.msgprint,
			throw=vmraid.throw,
			sendmail = vmraid.sendmail,
			get_print = vmraid.get_print,
			attach_print = vmraid.attach_print,

			user=user,
			get_fullname=vmraid.utils.get_fullname,
			get_gravatar=vmraid.utils.get_gravatar_url,
			full_name=vmraid.local.session.data.full_name if getattr(vmraid.local, "session", None) else "Guest",
			request=getattr(vmraid.local, 'request', {}),
			session=vmraid._dict(
				user=user,
				csrf_token=vmraid.local.session.data.csrf_token if getattr(vmraid.local, "session", None) else ''
			),
			make_get_request = vmraid.integrations.utils.make_get_request,
			make_post_request = vmraid.integrations.utils.make_post_request,
			socketio_port=vmraid.conf.socketio_port,
			get_hooks=vmraid.get_hooks,
			sanitize_html=vmraid.utils.sanitize_html,
			log_error=vmraid.log_error
		),
		VMRaidClient=VMRaidClient,
		style=vmraid._dict(
			border_color='#d1d8dd'
		),
		get_toc=get_toc,
		get_next_link=get_next_link,
		_=vmraid._,
		get_shade=get_shade,
		scrub=scrub,
		guess_mimetype=mimetypes.guess_type,
		html2text=html2text,
		dev_server=1 if vmraid._dev_server else 0,
		run_script=run_script
	)

	add_module_properties(vmraid.exceptions, out.vmraid, lambda obj: inspect.isclass(obj) and issubclass(obj, Exception))

	if not vmraid.flags.in_setup_help:
		out.get_visible_columns = get_visible_columns
		out.vmraid.date_format = date_format
		out.vmraid.time_format = time_format
		out.vmraid.db = NamespaceDict(
			get_list = vmraid.get_list,
			get_all = vmraid.get_all,
			get_value = vmraid.db.get_value,
			set_value = vmraid.db.set_value,
			get_single_value = vmraid.db.get_single_value,
			get_default = vmraid.db.get_default,
			escape = vmraid.db.escape,
			sql = read_sql
		)

	if vmraid.response:
		out.vmraid.response = vmraid.response

	out.update(safe_globals)

	# default writer allows write access
	out._write_ = _write
	out._getitem_ = _getitem

	# allow iterators and list comprehension
	out._getiter_ = iter
	out._iter_unpack_sequence_ = RestrictedPython.Guards.guarded_iter_unpack_sequence
	out.sorted = sorted

	return out

def read_sql(query, *args, **kwargs):
	'''a wrapper for vmraid.db.sql to allow reads'''
	if query.strip().split(None, 1)[0].lower() == 'select':
		return vmraid.db.sql(query, *args, **kwargs)
	else:
		raise vmraid.PermissionError('Only SELECT SQL allowed in scripting')

def run_script(script):
	'''run another server script'''
	return vmraid.get_doc('Server Script', script).execute_method()

def _getitem(obj, key):
	# guard function for RestrictedPython
	# allow any key to be accessed as long as it does not start with underscore
	if isinstance(key, str) and key.startswith('_'):
		raise SyntaxError('Key starts with _')
	return obj[key]

def _write(obj):
	# guard function for RestrictedPython
	# allow writing to any object
	return obj

def add_data_utils(data):
	for key, obj in vmraid.utils.data.__dict__.items():
		if key in VALID_UTILS:
			data[key] = obj

def add_module_properties(module, data, filter_method):
	for key, obj in module.__dict__.items():
		if key.startswith("_"):
			# ignore
			continue

		if filter_method(obj):
			# only allow functions
			data[key] = obj

VALID_UTILS = (
"DATE_FORMAT",
"TIME_FORMAT",
"DATETIME_FORMAT",
"is_invalid_date_string",
"getdate",
"get_datetime",
"to_timedelta",
"add_to_date",
"add_days",
"add_months",
"add_years",
"date_diff",
"month_diff",
"time_diff",
"time_diff_in_seconds",
"time_diff_in_hours",
"now_datetime",
"get_timestamp",
"get_eta",
"get_time_zone",
"convert_utc_to_user_timezone",
"now",
"nowdate",
"today",
"nowtime",
"get_first_day",
"get_quarter_start",
"get_first_day_of_week",
"get_year_start",
"get_last_day_of_week",
"get_last_day",
"get_time",
"get_datetime_in_timezone",
"get_datetime_str",
"get_date_str",
"get_time_str",
"get_user_date_format",
"get_user_time_format",
"format_date",
"format_time",
"format_datetime",
"format_duration",
"get_weekdays",
"get_weekday",
"get_timespan_date_range",
"global_date_format",
"has_common",
"flt",
"cint",
"floor",
"ceil",
"cstr",
"rounded",
"remainder",
"safe_div",
"round_based_on_smallest_currency_fraction",
"encode",
"parse_val",
"fmt_money",
"get_number_format_info",
"money_in_words",
"in_words",
"is_html",
"is_image",
"get_thumbnail_base64_for_image",
"image_to_base64",
"strip_html",
"escape_html",
"pretty_date",
"comma_or",
"comma_and",
"comma_sep",
"new_line_sep",
"filter_strip_join",
"get_url",
"get_host_name_from_request",
"url_contains_port",
"get_host_name",
"get_link_to_form",
"get_link_to_report",
"get_absolute_url",
"get_url_to_form",
"get_url_to_list",
"get_url_to_report",
"get_url_to_report_with_filters",
"evaluate_filters",
"compare",
"get_filter",
"make_filter_tuple",
"make_filter_dict",
"sanitize_column",
"scrub_urls",
"expand_relative_urls",
"quoted",
"quote_urls",
"unique",
"strip",
"to_markdown",
"md_to_html",
"markdown",
"is_subset",
"generate_hash",
"formatdate",
"get_user_info_for_avatar",
"get_abbr"
)
