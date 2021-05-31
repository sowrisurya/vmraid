import vmraid
from vmraid.desk.page.setup_wizard.install_fixtures import update_global_search_doctypes

def execute():
	vmraid.reload_doc("desk", "doctype", "global_search_doctype")
	vmraid.reload_doc("desk", "doctype", "global_search_settings")
	update_global_search_doctypes()