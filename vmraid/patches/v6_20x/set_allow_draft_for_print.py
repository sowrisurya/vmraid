from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.db.set_value("Print Settings", "Print Settings", "allow_print_for_draft", 1)