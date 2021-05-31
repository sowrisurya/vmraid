from __future__ import unicode_literals
import vmraid

def execute():
	if vmraid.db.exists('Module Def', 'Print'):
		vmraid.reload_doc('printing', 'doctype', 'print_format')
		vmraid.reload_doc('printing', 'doctype', 'print_settings')
		vmraid.reload_doc('printing', 'doctype', 'print_heading')
		vmraid.reload_doc('printing', 'doctype', 'letter_head')
		vmraid.reload_doc('printing', 'page', 'print_format_builder')
		vmraid.db.sql("""update `tabPrint Format` set module='Printing' where module='Print'""")
		
		vmraid.delete_doc('Module Def', 'Print')