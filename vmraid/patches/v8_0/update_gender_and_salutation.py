# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors

from __future__ import unicode_literals
import vmraid
from vmraid.desk.page.setup_wizard.install_fixtures import update_genders, update_salutations

def execute():
	vmraid.db.set_value("DocType", "Contact", "module", "Contacts")
	vmraid.db.set_value("DocType", "Address", "module", "Contacts")
	vmraid.db.set_value("DocType", "Address Template", "module", "Contacts")
	vmraid.reload_doc('contacts', 'doctype', 'gender')
	vmraid.reload_doc('contacts', 'doctype', 'salutation')

	update_genders()
	update_salutations()