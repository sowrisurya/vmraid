# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals, print_function
import vmraid

no_cache = 1

def get_context(context):
	if vmraid.flags.in_migrate: return
	print(vmraid.get_traceback().encode("utf-8"))
	return {"error": vmraid.get_traceback().replace("<", "&lt;").replace(">", "&gt;") }
