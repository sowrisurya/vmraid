from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.flags.in_patch = True
	vmraid.reload_doc('core', 'doctype', 'user_permission')
	vmraid.db.commit()
