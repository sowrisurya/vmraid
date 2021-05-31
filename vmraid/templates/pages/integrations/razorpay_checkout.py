# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals
import vmraid
from vmraid import _
from vmraid.utils import flt, cint
import json
from six import string_types

no_cache = 1

expected_keys = ('amount', 'title', 'description', 'reference_doctype', 'reference_docname',
	'payer_name', 'payer_email', 'order_id')

def get_context(context):
	context.no_cache = 1
	context.api_key = get_api_key()

	try:
		doc = vmraid.get_doc("Integration Request", vmraid.form_dict['token'])
		payment_details = json.loads(doc.data)

		for key in expected_keys:
			context[key] = payment_details[key]

		context['token'] = vmraid.form_dict['token']
		context['amount'] = flt(context['amount'])
		context['subscription_id'] = payment_details['subscription_id'] \
			if payment_details.get('subscription_id') else ''

	except Exception as e:
		vmraid.redirect_to_message(_('Invalid Token'),
			_('Seems token you are using is invalid!'),
			http_status_code=400, indicator_color='red')

		vmraid.local.flags.redirect_location = vmraid.local.response.location
		raise vmraid.Redirect

def get_api_key():
	api_key = vmraid.db.get_value("Razorpay Settings", None, "api_key")
	if cint(vmraid.form_dict.get("use_sandbox")):
		api_key = vmraid.conf.sandbox_api_key

	return api_key

@vmraid.whitelist(allow_guest=True)
def make_payment(razorpay_payment_id, options, reference_doctype, reference_docname, token):
	data = {}

	if isinstance(options, string_types):
		data = json.loads(options)

	data.update({
		"razorpay_payment_id": razorpay_payment_id,
		"reference_docname": reference_docname,
		"reference_doctype": reference_doctype,
		"token": token
	})

	data =  vmraid.get_doc("Razorpay Settings").create_request(data)
	vmraid.db.commit()
	return data
