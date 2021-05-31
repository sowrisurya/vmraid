# -*- coding: utf-8 -*-
# Copyright (c) 2020, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.model.document import Document
from vmraid import _

class NavbarSettings(Document):
	def validate(self):
		self.validate_standard_navbar_items()

	def validate_standard_navbar_items(self):
		doc_before_save = self.get_doc_before_save()

		before_save_items = [item for item in \
			doc_before_save.help_dropdown + doc_before_save.settings_dropdown if item.is_standard]

		after_save_items = [item for item in \
			self.help_dropdown + self.settings_dropdown if item.is_standard]

		if not vmraid.flags.in_patch and (len(before_save_items) > len(after_save_items)):
			vmraid.throw(_("Please hide the standard navbar items instead of deleting them"))

@vmraid.whitelist(allow_guest=True)
def get_app_logo():
	app_logo = vmraid.db.get_single_value('Navbar Settings', 'app_logo', cache=True)
	if not app_logo:
		app_logo = vmraid.get_hooks('app_logo_url')[-1]

	return app_logo

def get_navbar_settings():
	navbar_settings = vmraid.get_single('Navbar Settings')
	return navbar_settings




