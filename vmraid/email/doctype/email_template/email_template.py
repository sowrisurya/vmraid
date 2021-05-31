# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid, json
from vmraid.model.document import Document
from vmraid.utils.jinja import validate_template
from six import string_types

class EmailTemplate(Document):
	def validate(self):
		if self.use_html:
			validate_template(self.response_html)
		else:
			validate_template(self.response)

	def get_formatted_subject(self, doc):
		return vmraid.render_template(self.subject, doc)

	def get_formatted_response(self, doc):
		if self.use_html:
			return vmraid.render_template(self.response_html, doc)

		return vmraid.render_template(self.response, doc)

	def get_formatted_email(self, doc):
		if isinstance(doc, string_types):
			doc = json.loads(doc)

		return {
			"subject" : self.get_formatted_subject(doc),
			"message" : self.get_formatted_response(doc)
		}


@vmraid.whitelist()
def get_email_template(template_name, doc):
	'''Returns the processed HTML of a email template with the given doc'''
	if isinstance(doc, string_types):
		doc = json.loads(doc)

	email_template = vmraid.get_doc("Email Template", template_name)
	return email_template.get_formatted_email(doc)