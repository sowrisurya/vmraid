# Copyright (c) 2020, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid


def execute():
	vmraid.delete_doc("DocType", "Package Publish Tool", ignore_missing=True)
	vmraid.delete_doc("DocType", "Package Document Type", ignore_missing=True)
	vmraid.delete_doc("DocType", "Package Publish Target", ignore_missing=True)
