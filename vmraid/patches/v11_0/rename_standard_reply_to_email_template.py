from __future__ import unicode_literals
import vmraid
from vmraid.model.rename_doc import rename_doc

def execute():
	if vmraid.db.table_exists("Standard Reply") and not vmraid.db.table_exists("Email Template"):
		rename_doc('DocType', 'Standard Reply', 'Email Template')
		vmraid.reload_doc('email', 'doctype', 'email_template')
