# -*- coding: utf-8 -*-
# Copyright (c) 2015, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.model.document import Document

class OAuthBearerToken(Document):
	def validate(self):
		if not self.expiration_time:
			self.expiration_time = vmraid.utils.datetime.datetime.strptime(self.creation, "%Y-%m-%d %H:%M:%S.%f") + vmraid.utils.datetime.timedelta(seconds=self.expires_in)

