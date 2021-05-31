# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals

def execute():
	from vmraid.installer import remove_from_installed_apps
	remove_from_installed_apps("shopping_cart")
