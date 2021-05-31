# -*- coding: utf-8 -*-
# Copyright (c) 2015, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.model.document import Document

class EmailGroupMember(Document):
	def after_delete(self):
		email_group = vmraid.get_doc('Email Group', self.email_group)
		email_group.update_total_subscribers()

	def after_insert(self):
		email_group = vmraid.get_doc('Email Group', self.email_group)
		email_group.update_total_subscribers()

def after_doctype_insert():
	vmraid.db.add_unique("Email Group Member", ("email_group", "email"))
