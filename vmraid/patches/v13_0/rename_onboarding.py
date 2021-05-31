# Copyright (c) 2020, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	if vmraid.db.exists("DocType", "Onboarding"):
		vmraid.rename_doc("DocType", "Onboarding", "Module Onboarding", ignore_if_exists=True)

