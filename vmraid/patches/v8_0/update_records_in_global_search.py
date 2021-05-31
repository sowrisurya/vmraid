from __future__ import unicode_literals
import vmraid
from vmraid.utils.global_search import get_doctypes_with_global_search, rebuild_for_doctype
from vmraid.utils import update_progress_bar

def execute():
	vmraid.cache().delete_value('doctypes_with_global_search')
	doctypes_with_global_search = get_doctypes_with_global_search(with_child_tables=False)
	
	for i, doctype in enumerate(doctypes_with_global_search):
		update_progress_bar("Updating Global Search", i, len(doctypes_with_global_search))
		rebuild_for_doctype(doctype)
