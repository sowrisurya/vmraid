from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.rename_doc('DocType', 'Newsletter List', 'Email Group')
	vmraid.rename_doc('DocType', 'Newsletter List Subscriber', 'Email Group Member')