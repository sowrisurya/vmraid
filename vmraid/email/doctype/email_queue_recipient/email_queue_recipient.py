# -*- coding: utf-8 -*-
# Copyright (c) 2015, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.model.document import Document

class EmailQueueRecipient(Document):
	DOCTYPE = 'Email Queue Recipient'

	def is_mail_to_be_sent(self):
		return self.status == 'Not Sent'

	def is_main_sent(self):
		return self.status == 'Sent'

	def update_db(self, commit=False, **kwargs):
		vmraid.db.set_value(self.DOCTYPE, self.name, kwargs)
		if commit:
			vmraid.db.commit()

