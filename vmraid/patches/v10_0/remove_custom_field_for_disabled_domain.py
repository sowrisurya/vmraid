from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc("core", "doctype", "domain")
	vmraid.reload_doc("core", "doctype", "has_domain")
	active_domains = vmraid.get_active_domains()
	all_domains = vmraid.get_all("Domain")

	for d in all_domains:
		if d.name not in active_domains:
			inactive_domain = vmraid.get_doc("Domain", d.name)
			inactive_domain.setup_data()
			inactive_domain.remove_custom_field()
