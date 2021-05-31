from __future__ import unicode_literals
import vmraid
from vmraid.permissions import setup_custom_perms
from vmraid.core.page.permission_manager.permission_manager import get_standard_permissions
from vmraid.utils.reset_doc import setup_perms_for

'''
Copy DocPerm to Custom DocPerm where permissions are set differently
'''

def execute():
	for d in vmraid.db.get_all('DocType', dict(istable=0, issingle=0, custom=0)):
		setup_perms_for(d.name)
