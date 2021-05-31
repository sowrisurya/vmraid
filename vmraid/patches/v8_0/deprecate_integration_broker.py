from __future__ import unicode_literals
import vmraid
from vmraid.integrations.utils import create_payment_gateway

def execute():
	setup_enabled_integrations()

	for doctype in ["integration_request", "oauth_authorization_code", "oauth_bearer_token", "oauth_client"]:
		vmraid.reload_doc('integrations', 'doctype', doctype)
	
	vmraid.reload_doc("core", "doctype", "payment_gateway")
	update_doctype_module()
	create_payment_gateway_master_records()

	for doctype in ["Integration Service", "Integration Service Parameter"]:
		vmraid.delete_doc("DocType", doctype)
	
	if not vmraid.db.get_value("DocType", {"module": "Integration Broker"}, "name"):
		vmraid.delete_doc("Module Def", "Integration Broker")

def setup_enabled_integrations():
	if not vmraid.db.exists("DocType", "Integration Service"):
		return

	for service in vmraid.get_all("Integration Service",
		filters={"enabled": 1, "service": ('in', ("Dropbox", "LDAP"))}, fields=["name"]):

		doctype = "{0} Settings".format(service.name)
		vmraid.db.set_value(doctype, doctype, 'enabled', 1)

def update_doctype_module():
	vmraid.db.sql("""update tabDocType set module='Integrations'
		where name in ('Integration Request', 'Oauth Authorization Code',
			'Oauth Bearer Token', 'Oauth Client') """)

	vmraid.db.sql(""" update tabDocType set module='Core' where name = 'Payment Gateway'""")

def create_payment_gateway_master_records():
	for payment_gateway in ["Razorpay", "PayPal"]:
		doctype = "{0} Settings".format(payment_gateway)
		doc = vmraid.get_doc(doctype)
		doc_meta = vmraid.get_meta(doctype)
		all_mandatory_fields_has_value = True

		for d in doc_meta.fields:
			if d.reqd and not doc.get(d.fieldname):
				all_mandatory_fields_has_value = False
				break

		if all_mandatory_fields_has_value:
			create_payment_gateway(payment_gateway)
