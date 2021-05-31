# -*- coding: utf-8 -*-
# Copyright (c) 2019, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from vmraid.model.document import Document

class WebsiteRouteMeta(Document):
	def autoname(self):
		if self.name and self.name.startswith('/'):
			self.name = self.name[1:]
