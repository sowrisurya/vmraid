# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
        vmraid.delete_doc_if_exists("DocType", "User Permission for Page and Report")