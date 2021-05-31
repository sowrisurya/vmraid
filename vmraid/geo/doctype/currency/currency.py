# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# License: See license.txt

from __future__ import unicode_literals
import vmraid
from vmraid import throw, _

from vmraid.model.document import Document

class Currency(Document):
	def validate(self):
		if not vmraid.flags.in_install_app:
			vmraid.clear_cache()
