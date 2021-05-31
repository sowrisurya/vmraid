# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals, print_function

no_cache = 1
base_template_path = "templates/www/app.html"

import os, re
import vmraid
from vmraid import _
import vmraid.sessions

def get_context(context):
	if vmraid.session.user == "Guest":
		vmraid.throw(_("Log in to access this page."), vmraid.PermissionError)
	elif vmraid.db.get_value("User", vmraid.session.user, "user_type") == "Website User":
		vmraid.throw(_("You are not permitted to access this page."), vmraid.PermissionError)

	hooks = vmraid.get_hooks()
	try:
		boot = vmraid.sessions.get()
	except Exception as e:
		boot = vmraid._dict(status='failed', error = str(e))
		print(vmraid.get_traceback())

	# this needs commit
	csrf_token = vmraid.sessions.get_csrf_token()

	vmraid.db.commit()

	desk_theme = vmraid.db.get_value("User", vmraid.session.user, "desk_theme")

	boot_json = vmraid.as_json(boot)

	# remove script tags from boot
	boot_json = re.sub(r"\<script[^<]*\</script\>", "", boot_json)

	# TODO: Find better fix
	boot_json = re.sub(r"</script\>", "", boot_json)

	context.update({
		"no_cache": 1,
		"build_version": vmraid.utils.get_build_version(),
		"include_js": hooks["app_include_js"],
		"include_css": hooks["app_include_css"],
		"sounds": hooks["sounds"],
		"boot": boot if context.get("for_mobile") else boot_json,
		"desk_theme": desk_theme or "Light",
		"csrf_token": csrf_token,
		"google_analytics_id": vmraid.conf.get("google_analytics_id"),
		"google_analytics_anonymize_ip": vmraid.conf.get("google_analytics_anonymize_ip"),
		"mixpanel_id": vmraid.conf.get("mixpanel_id")
	})

	return context

@vmraid.whitelist()
def get_desk_assets(build_version):
	"""Get desk assets to be loaded for mobile app"""
	data = get_context({"for_mobile": True})
	assets = [{"type": "js", "data": ""}, {"type": "css", "data": ""}]

	if build_version != data["build_version"]:
		# new build, send assets
		for path in data["include_js"]:
			# assets path shouldn't start with /
			# as it points to different location altogether
			if path.startswith('/assets/'):
				path = path.replace('/assets/', 'assets/')
			try:
				with open(os.path.join(vmraid.local.sites_path, path) ,"r") as f:
					assets[0]["data"] = assets[0]["data"] + "\n" + vmraid.safe_decode(f.read(), "utf-8")
			except IOError:
				pass

		for path in data["include_css"]:
			if path.startswith('/assets/'):
				path = path.replace('/assets/', 'assets/')
			try:
				with open(os.path.join(vmraid.local.sites_path, path) ,"r") as f:
					assets[1]["data"] = assets[1]["data"] + "\n" + vmraid.safe_decode(f.read(), "utf-8")
			except IOError:
				pass

	return {
		"build_version": data["build_version"],
		"boot": data["boot"],
		"assets": assets
	}
