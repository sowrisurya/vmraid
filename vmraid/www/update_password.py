# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

from vmraid import _

no_cache = 1

def get_context(context):
	context.no_breadcrumbs = True
	context.parents = [{"name":"me", "title":_("My Account")}]
