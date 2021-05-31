# -*- coding: utf-8 -*-
# Copyright (c) 2015, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.model.document import Document

class HasRole(Document):
	def before_insert(self):
		if vmraid.db.exists("Has Role", {"parent": self.parent, "role": self.role}):
			vmraid.throw(vmraid._("User '{0}' already has the role '{1}'").format(self.parent, self.role))
