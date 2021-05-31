# -*- coding: utf-8 -*-
# Copyright (c) 2020, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from vmraid.model.document import Document

class ModuleProfile(Document):
	def onload(self):
		from vmraid.config import get_modules_from_all_apps
		self.set_onload('all_modules',
			[m.get("module_name") for m in get_modules_from_all_apps()])
