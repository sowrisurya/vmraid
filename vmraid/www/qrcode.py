# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import vmraid
from vmraid import _
from six.moves.urllib.parse import parse_qsl
from vmraid.twofactor import get_qr_svg_code

def get_context(context):
	context.no_cache = 1
	context.qr_code_user,context.qrcode_svg = get_user_svg_from_cache()

def get_query_key():
	'''Return query string arg.'''
	query_string = vmraid.local.request.query_string
	query = dict(parse_qsl(query_string))
	query = {key.decode(): val.decode() for key, val in query.items()}
	if not 'k' in list(query):
		vmraid.throw(_('Not Permitted'),vmraid.PermissionError)
	query = (query['k']).strip()
	if False in [i.isalpha() or i.isdigit() for i in query]:
		vmraid.throw(_('Not Permitted'),vmraid.PermissionError)
	return query

def get_user_svg_from_cache():
	'''Get User and SVG code from cache.'''
	key = get_query_key()
	totp_uri = vmraid.cache().get_value("{}_uri".format(key))
	user = vmraid.cache().get_value("{}_user".format(key))
	if not totp_uri or not user:
		vmraid.throw(_('Page has expired!'),vmraid.PermissionError)
	if not vmraid.db.exists('User',user):
		vmraid.throw(_('Not Permitted'), vmraid.PermissionError)
	user = vmraid.get_doc('User',user)
	svg = get_qr_svg_code(totp_uri)
	return (user,svg.decode())
