# -*- coding: utf-8 -*-
# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.model.document import Document
from vmraid import _

class EmailUnsubscribe(Document):
	def validate(self):
		if not self.global_unsubscribe and not (self.reference_doctype and self.reference_name):
			vmraid.throw(_("Reference DocType and Reference Name are required"), vmraid.MandatoryError)

		if not self.global_unsubscribe and vmraid.db.get_value(self.doctype, self.name, "global_unsubscribe"):
			vmraid.throw(_("Delete this record to allow sending to this email address"))

		if self.global_unsubscribe:
			if vmraid.get_all("Email Unsubscribe",
				filters={"email": self.email, "global_unsubscribe": 1, "name": ["!=", self.name]}):
				vmraid.throw(_("{0} already unsubscribed").format(self.email), vmraid.DuplicateEntryError)

		else:
			if vmraid.get_all("Email Unsubscribe",
				filters={
					"email": self.email,
					"reference_doctype": self.reference_doctype,
					"reference_name": self.reference_name,
					"name": ["!=", self.name]
				}):
				vmraid.throw(_("{0} already unsubscribed for {1} {2}").format(
					self.email, self.reference_doctype, self.reference_name),
					vmraid.DuplicateEntryError)

	def on_update(self):
		if self.reference_doctype and self.reference_name:
			doc = vmraid.get_doc(self.reference_doctype, self.reference_name)
			doc.add_comment("Label", _("Left this conversation"), comment_email=self.email)

