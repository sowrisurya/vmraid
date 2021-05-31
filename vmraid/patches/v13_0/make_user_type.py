import vmraid
from vmraid.utils.install import create_user_type

def execute():
	vmraid.reload_doc('core', 'doctype', 'role')
	vmraid.reload_doc('core', 'doctype', 'user_document_type')
	vmraid.reload_doc('core', 'doctype', 'user_type_module')
	vmraid.reload_doc('core', 'doctype', 'user_select_document_type')
	vmraid.reload_doc('core', 'doctype', 'user_type')


	create_user_type()
