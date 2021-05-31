# Copyright (c) 2020, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid


def execute():
	vmraid.reload_doc("website", "doctype", "website_theme_ignore_app")
	themes = vmraid.db.get_all(
		"Website Theme", filters={"theme_url": ("not like", "/files/website_theme/%")}
	)
	for theme in themes:
		doc = vmraid.get_doc("Website Theme", theme.name)
		try:
			doc.generate_bootstrap_theme()
			doc.save()
		except: # noqa: E722
			print('Ignoring....')
			print(vmraid.get_traceback())
