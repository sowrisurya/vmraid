# -*- coding: utf-8 -*-
# Copyright (c) 2020, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.model.document import Document

class InstalledApplications(Document):
	def update_versions(self):
		self.delete_key("installed_applications")
		for app in vmraid.utils.get_installed_apps_info():
			self.append("installed_applications", {
				"app_name": app.get("app_name"),
				"app_version": app.get("version") or "UNVERSIONED",
				"git_branch": app.get("branch") or "UNVERSIONED"
			})
		self.save()