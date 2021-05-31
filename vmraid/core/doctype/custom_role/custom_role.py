# -*- coding: utf-8 -*-
# Copyright (c) 2015, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.model.document import Document

class CustomRole(Document):
	def validate(self):
		if self.report and not self.ref_doctype:
			self.ref_doctype = vmraid.db.get_value('Report', self.report, 'ref_doctype')

def get_custom_allowed_roles(field, name):
	allowed_roles = []
	custom_role = vmraid.db.get_value('Custom Role', {field: name}, 'name')
	if custom_role:
		custom_role_doc = vmraid.get_doc('Custom Role', custom_role)
		allowed_roles = [d.role for d in custom_role_doc.roles]

	return allowed_roles