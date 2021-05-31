# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# See license.txt

from __future__ import unicode_literals
import vmraid

def get_context(context):
	token = vmraid.local.form_dict.token

	if token:
		vmraid.db.set_value("Integration Request", token, "status", "Cancelled")
		vmraid.db.commit()
