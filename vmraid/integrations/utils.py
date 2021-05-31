# -*- coding: utf-8 -*-
# Copyright (c) 2019, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
import json,datetime
from six.moves.urllib.parse import parse_qs
from six import string_types, text_type
from vmraid.utils import get_request_session
from vmraid import _

def make_get_request(url, auth=None, headers=None, data=None):
	if not auth:
		auth = ''
	if not data:
		data = {}
	if not headers:
		headers = {}

	try:
		s = get_request_session()
		vmraid.flags.integration_request = s.get(url, data={}, auth=auth, headers=headers)
		vmraid.flags.integration_request.raise_for_status()
		return vmraid.flags.integration_request.json()

	except Exception as exc:
		vmraid.log_error(vmraid.get_traceback())
		raise exc

def make_post_request(url, auth=None, headers=None, data=None):
	if not auth:
		auth = ''
	if not data:
		data = {}
	if not headers:
		headers = {}

	try:
		s = get_request_session()
		vmraid.flags.integration_request = s.post(url, data=data, auth=auth, headers=headers)
		vmraid.flags.integration_request.raise_for_status()

		if vmraid.flags.integration_request.headers.get("content-type") == "text/plain; charset=utf-8":
			return parse_qs(vmraid.flags.integration_request.text)

		return vmraid.flags.integration_request.json()
	except Exception as exc:
		vmraid.log_error()
		raise exc

def create_request_log(data, integration_type, service_name, name=None, error=None):
	if isinstance(data, string_types):
		data = json.loads(data)

	if isinstance(error, string_types):
		error = json.loads(error)

	integration_request = vmraid.get_doc({
		"doctype": "Integration Request",
		"integration_type": integration_type,
		"integration_request_service": service_name,
		"reference_doctype": data.get("reference_doctype"),
		"reference_docname": data.get("reference_docname"),
		"error": json.dumps(error, default=json_handler),
		"data": json.dumps(data, default=json_handler)
	})

	if name:
		integration_request.flags._name = name

	integration_request.insert(ignore_permissions=True)
	vmraid.db.commit()

	return integration_request

def get_payment_gateway_controller(payment_gateway):
	'''Return payment gateway controller'''
	gateway = vmraid.get_doc("Payment Gateway", payment_gateway)
	if gateway.gateway_controller is None:
		try:
			return vmraid.get_doc("{0} Settings".format(payment_gateway))
		except Exception:
			vmraid.throw(_("{0} Settings not found").format(payment_gateway))
	else:
		try:
			return vmraid.get_doc(gateway.gateway_settings, gateway.gateway_controller)
		except Exception:
			vmraid.throw(_("{0} Settings not found").format(payment_gateway))


@vmraid.whitelist(allow_guest=True, xss_safe=True)
def get_checkout_url(**kwargs):
	try:
		if kwargs.get('payment_gateway'):
			doc = vmraid.get_doc("{0} Settings".format(kwargs.get('payment_gateway')))
			return doc.get_payment_url(**kwargs)
		else:
			raise Exception
	except Exception:
		vmraid.respond_as_web_page(_("Something went wrong"),
			_("Looks like something is wrong with this site's payment gateway configuration. No payment has been made."),
			indicator_color='red',
			http_status_code=vmraid.ValidationError.http_status_code)

def create_payment_gateway(gateway, settings=None, controller=None):
	# NOTE: we don't translate Payment Gateway name because it is an internal doctype
	if not vmraid.db.exists("Payment Gateway", gateway):
		payment_gateway = vmraid.get_doc({
			"doctype": "Payment Gateway",
			"gateway": gateway,
			"gateway_settings": settings,
			"gateway_controller": controller
		})
		payment_gateway.insert(ignore_permissions=True)

def json_handler(obj):
	if isinstance(obj, (datetime.date, datetime.timedelta, datetime.datetime)):
		return text_type(obj)
