# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import base64
import binascii
import json
from urllib.parse import urlencode, urlparse

import vmraid
import vmraid.client
import vmraid.handler
from vmraid import _
from vmraid.utils.response import build_response
from vmraid.utils.data import sbool


def handle():
	"""
	Handler for `/api` methods

	### Examples:

	`/api/method/{methodname}` will call a whitelisted method

	`/api/resource/{doctype}` will query a table
		examples:
		- `?fields=["name", "owner"]`
		- `?filters=[["Task", "name", "like", "%005"]]`
		- `?limit_start=0`
		- `?limit_page_length=20`

	`/api/resource/{doctype}/{name}` will point to a resource
		`GET` will return doclist
		`POST` will insert
		`PUT` will update
		`DELETE` will delete

	`/api/resource/{doctype}/{name}?run_method={method}` will run a whitelisted controller method
	"""

	parts = vmraid.request.path[1:].split("/",3)
	call = doctype = name = None

	if len(parts) > 1:
		call = parts[1]

	if len(parts) > 2:
		doctype = parts[2]

	if len(parts) > 3:
		name = parts[3]

	if call=="method":
		vmraid.local.form_dict.cmd = doctype
		return vmraid.handler.handle()

	elif call=="resource":
		if "run_method" in vmraid.local.form_dict:
			method = vmraid.local.form_dict.pop("run_method")
			doc = vmraid.get_doc(doctype, name)
			doc.is_whitelisted(method)

			if vmraid.local.request.method=="GET":
				if not doc.has_permission("read"):
					vmraid.throw(_("Not permitted"), vmraid.PermissionError)
				vmraid.local.response.update({"data": doc.run_method(method, **vmraid.local.form_dict)})

			if vmraid.local.request.method=="POST":
				if not doc.has_permission("write"):
					vmraid.throw(_("Not permitted"), vmraid.PermissionError)

				vmraid.local.response.update({"data": doc.run_method(method, **vmraid.local.form_dict)})
				vmraid.db.commit()

		else:
			if name:
				if vmraid.local.request.method=="GET":
					doc = vmraid.get_doc(doctype, name)
					if not doc.has_permission("read"):
						raise vmraid.PermissionError
					vmraid.local.response.update({"data": doc})

				if vmraid.local.request.method=="PUT":
					data = get_request_form_data()

					doc = vmraid.get_doc(doctype, name)

					if "flags" in data:
						del data["flags"]

					# Not checking permissions here because it's checked in doc.save
					doc.update(data)

					vmraid.local.response.update({
						"data": doc.save().as_dict()
					})

					if doc.parenttype and doc.parent:
						vmraid.get_doc(doc.parenttype, doc.parent).save()

					vmraid.db.commit()

				if vmraid.local.request.method == "DELETE":
					# Not checking permissions here because it's checked in delete_doc
					vmraid.delete_doc(doctype, name, ignore_missing=False)
					vmraid.local.response.http_status_code = 202
					vmraid.local.response.message = "ok"
					vmraid.db.commit()

			elif doctype:
				if vmraid.local.request.method == "GET":
					# set fields for vmraid.get_list
					if vmraid.local.form_dict.get("fields"):
						vmraid.local.form_dict["fields"] = json.loads(vmraid.local.form_dict["fields"])

					# set limit of records for vmraid.get_list
					vmraid.local.form_dict.setdefault(
						"limit_page_length",
						vmraid.local.form_dict.limit or vmraid.local.form_dict.limit_page_length or 20,
					)

					# convert strings to native types - only as_dict and debug accept bool
					for param in ["as_dict", "debug"]:
						param_val = vmraid.local.form_dict.get(param)
						if param_val is not None:
							vmraid.local.form_dict[param] = sbool(param_val)

					# evaluate vmraid.get_list
					data = vmraid.call(vmraid.client.get_list, doctype, **vmraid.local.form_dict)

					# set vmraid.get_list result to response
					vmraid.local.response.update({"data": data})

				if vmraid.local.request.method == "POST":
					# fetch data from from dict
					data = get_request_form_data()
					data.update({"doctype": doctype})

					# insert document from request data
					doc = vmraid.get_doc(data).insert()

					# set response data
					vmraid.local.response.update({"data": doc.as_dict()})

					# commit for POST requests
					vmraid.db.commit()
			else:
				raise vmraid.DoesNotExistError

	else:
		raise vmraid.DoesNotExistError

	return build_response("json")


def get_request_form_data():
	if vmraid.local.form_dict.data is None:
		data = vmraid.safe_decode(vmraid.local.request.get_data())
	else:
		data = vmraid.local.form_dict.data

	return vmraid.parse_json(data)


def validate_auth():
	"""
	Authenticate and sets user for the request.
	"""
	authorization_header = vmraid.get_request_header("Authorization", str()).split(" ")

	if len(authorization_header) == 2:
		validate_oauth(authorization_header)
		validate_auth_via_api_keys(authorization_header)

	validate_auth_via_hooks()


def validate_oauth(authorization_header):
	"""
	Authenticate request using OAuth and set session user

	Args:
		authorization_header (list of str): The 'Authorization' header containing the prefix and token
	"""

	from vmraid.integrations.oauth2 import get_oauth_server
	from vmraid.oauth import get_url_delimiter

	form_dict = vmraid.local.form_dict
	token = authorization_header[1]
	req = vmraid.request
	parsed_url = urlparse(req.url)
	access_token = {"access_token": token}
	uri = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path + "?" + urlencode(access_token)
	http_method = req.method
	headers = req.headers
	body = req.get_data()
	if req.content_type and "multipart/form-data" in req.content_type:
		body = None

	try:
		required_scopes = vmraid.db.get_value("OAuth Bearer Token", token, "scopes").split(get_url_delimiter())
		valid, oauthlib_request = get_oauth_server().verify_request(uri, http_method, body, headers, required_scopes)
		if valid:
			vmraid.set_user(vmraid.db.get_value("OAuth Bearer Token", token, "user"))
			vmraid.local.form_dict = form_dict
	except AttributeError:
		pass



def validate_auth_via_api_keys(authorization_header):
	"""
	Authenticate request using API keys and set session user

	Args:
		authorization_header (list of str): The 'Authorization' header containing the prefix and token
	"""

	try:
		auth_type, auth_token = authorization_header
		authorization_source = vmraid.get_request_header("VMRaid-Authorization-Source")
		if auth_type.lower() == 'basic':
			api_key, api_secret = vmraid.safe_decode(base64.b64decode(auth_token)).split(":")
			validate_api_key_secret(api_key, api_secret, authorization_source)
		elif auth_type.lower() == 'token':
			api_key, api_secret = auth_token.split(":")
			validate_api_key_secret(api_key, api_secret, authorization_source)
	except binascii.Error:
		vmraid.throw(_("Failed to decode token, please provide a valid base64-encoded token."), vmraid.InvalidAuthorizationToken)
	except (AttributeError, TypeError, ValueError):
		pass


def validate_api_key_secret(api_key, api_secret, vmraid_authorization_source=None):
	"""vmraid_authorization_source to provide api key and secret for a doctype apart from User"""
	doctype = vmraid_authorization_source or 'User'
	doc = vmraid.db.get_value(
		doctype=doctype,
		filters={"api_key": api_key},
		fieldname=["name"]
	)
	form_dict = vmraid.local.form_dict
	doc_secret = vmraid.utils.password.get_decrypted_password(doctype, doc, fieldname='api_secret')
	if api_secret == doc_secret:
		if doctype == 'User':
			user = vmraid.db.get_value(
				doctype="User",
				filters={"api_key": api_key},
				fieldname=["name"]
			)
		else:
			user = vmraid.db.get_value(doctype, doc, 'user')
		if vmraid.local.login_manager.user in ('', 'Guest'):
			vmraid.set_user(user)
		vmraid.local.form_dict = form_dict


def validate_auth_via_hooks():
	for auth_hook in vmraid.get_hooks('auth_hooks', []):
		vmraid.get_attr(auth_hook)()
