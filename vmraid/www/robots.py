from __future__ import unicode_literals
import vmraid

base_template_path = "templates/www/robots.txt"

def get_context(context):
	robots_txt = (
		vmraid.db.get_single_value('Website Settings', 'robots_txt') or
		(vmraid.local.conf.robots_txt and vmraid.read_file(vmraid.local.conf.robots_txt)) or '')

	return { 'robots_txt': robots_txt }
