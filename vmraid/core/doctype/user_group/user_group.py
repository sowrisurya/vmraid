# -*- coding: utf-8 -*-
# Copyright (c) 2021, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import vmraid
from vmraid.model.document import Document
import vmraid

class UserGroup(Document):
	def after_insert(self):
		vmraid.cache().delete_key('user_groups')

	def on_trash(self):
		vmraid.cache().delete_key('user_groups')
