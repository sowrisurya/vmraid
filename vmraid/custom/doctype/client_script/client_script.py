# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals
import vmraid

from vmraid import _
from vmraid.model.document import Document


class ClientScript(Document):
	def autoname(self):
		self.name = f"{self.dt}-{self.view}"

	def validate(self):
		if not self.is_new():
			return

		exists = vmraid.db.exists(
			"Client Script", {"dt": self.dt, "view": self.view}
		)
		if exists:
			vmraid.throw(
				_("Client Script for {0} {1} already exists").format(vmraid.bold(self.dt), self.view),
				vmraid.DuplicateEntryError,
			)

	def on_update(self):
		vmraid.clear_cache(doctype=self.dt)

	def on_trash(self):
		vmraid.clear_cache(doctype=self.dt)
