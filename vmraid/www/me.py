# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid
from vmraid import _
import vmraid.www.list

no_cache = 1

def get_context(context):
	if vmraid.session.user=='Guest':
		vmraid.throw(_("You need to be logged in to access this page"), vmraid.PermissionError)

	context.show_sidebar=True