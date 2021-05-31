from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doctype('Print Settings')
	vmraid.db.set_value('Print Settings', 'Print Settings', 'repeat_header_footer', 1)
