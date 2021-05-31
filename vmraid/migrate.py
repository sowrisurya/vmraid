# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import json
import os
import sys
import vmraid
import vmraid.translate
import vmraid.modules.patch_handler
import vmraid.model.sync
from vmraid.utils.fixtures import sync_fixtures
from vmraid.utils.connections import check_connection
from vmraid.utils.dashboard import sync_dashboards
from vmraid.cache_manager import clear_global_cache
from vmraid.desk.notifications import clear_notifications
from vmraid.website import render
from vmraid.core.doctype.language.language import sync_languages
from vmraid.modules.utils import sync_customizations
from vmraid.core.doctype.scheduled_job_type.scheduled_job_type import sync_jobs
from vmraid.search.website_search import build_index_for_all_routes


def migrate(verbose=True, skip_failing=False, skip_search_index=False):
	'''Migrate all apps to the current version, will:
	- run before migrate hooks
	- run patches
	- sync doctypes (schema)
	- sync dashboards
	- sync fixtures
	- sync desktop icons
	- sync web pages (from /www)
	- sync web pages (from /www)
	- run after migrate hooks
	'''

	service_status = check_connection(redis_services=["redis_cache"])
	if False in service_status.values():
		for service in service_status:
			if not service_status.get(service, True):
				print("{} service is not running.".format(service))
		print("""Cannot run bench migrate without the services running.
If you are running bench in development mode, make sure that bench is running:

$ bench start

Otherwise, check the server logs and ensure that all the required services are running.""")
		sys.exit(1)

	touched_tables_file = vmraid.get_site_path('touched_tables.json')
	if os.path.exists(touched_tables_file):
		os.remove(touched_tables_file)

	try:
		vmraid.flags.touched_tables = set()
		vmraid.flags.in_migrate = True

		clear_global_cache()

		#run before_migrate hooks
		for app in vmraid.get_installed_apps():
			for fn in vmraid.get_hooks('before_migrate', app_name=app):
				vmraid.get_attr(fn)()

		# run patches
		vmraid.modules.patch_handler.run_all(skip_failing)

		# sync
		vmraid.model.sync.sync_all(verbose=verbose)
		vmraid.translate.clear_cache()
		sync_jobs()
		sync_fixtures()
		sync_dashboards()
		sync_customizations()
		sync_languages()

		vmraid.get_doc('Portal Settings', 'Portal Settings').sync_menu()

		# syncs statics
		render.clear_cache()

		# updating installed applications data
		vmraid.get_single('Installed Applications').update_versions()

		#run after_migrate hooks
		for app in vmraid.get_installed_apps():
			for fn in vmraid.get_hooks('after_migrate', app_name=app):
				vmraid.get_attr(fn)()

		# build web_routes index
		if not skip_search_index:
			# Run this last as it updates the current session
			print('Building search index for {}'.format(vmraid.local.site))
			build_index_for_all_routes()

		vmraid.db.commit()

		clear_notifications()

		vmraid.publish_realtime("version-update")
		vmraid.flags.in_migrate = False
	finally:
		with open(touched_tables_file, 'w') as f:
			json.dump(list(vmraid.flags.touched_tables), f, sort_keys=True, indent=4)
		vmraid.flags.touched_tables.clear()
