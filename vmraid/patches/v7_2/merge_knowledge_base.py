from __future__ import unicode_literals
import vmraid

from vmraid.patches.v7_0.re_route import update_routes
from vmraid.installer import remove_from_installed_apps

def execute():
	if 'knowledge_base' in vmraid.get_installed_apps():
		vmraid.reload_doc('website', 'doctype', 'help_category')
		vmraid.reload_doc('website', 'doctype', 'help_article')
		update_routes(['Help Category', 'Help Article'])
		remove_from_installed_apps('knowledge_base')

		# remove module def
		if vmraid.db.exists('Module Def', 'Knowledge Base'):
			vmraid.delete_doc('Module Def', 'Knowledge Base')

		# set missing routes
		for doctype in ('Help Category', 'Help Article'):
			for d in vmraid.get_all(doctype, fields=['name', 'route']):
				if not d.route:
					doc = vmraid.get_doc(doctype, d.name)
					doc.set_route()
					doc.db_update()