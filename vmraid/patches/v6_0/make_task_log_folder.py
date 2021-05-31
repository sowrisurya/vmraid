from __future__ import unicode_literals
import vmraid.utils, os

def execute():
	path = vmraid.utils.get_site_path('task-logs')
	if not os.path.exists(path):
		os.makedirs(path)
