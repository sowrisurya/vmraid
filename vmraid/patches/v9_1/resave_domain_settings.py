from __future__ import unicode_literals
import vmraid

def execute():
	domain_settings = vmraid.get_doc('Domain Settings')
	active_domains = [d.domain for d in domain_settings.active_domains]
	try:
		for d in ('Education', 'Healthcare', 'Hospitality'):
			if d in active_domains and vmraid.db.exists('Domain', d):
				domain = vmraid.get_doc('Domain', d)
				domain.setup_domain()
	except vmraid.LinkValidationError:
		pass
