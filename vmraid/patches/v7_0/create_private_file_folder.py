from __future__ import unicode_literals
import vmraid, os

def execute():
	if not os.path.exists(os.path.join(vmraid.local.site_path, 'private', 'files')):
		vmraid.create_folder(os.path.join(vmraid.local.site_path, 'private', 'files'))