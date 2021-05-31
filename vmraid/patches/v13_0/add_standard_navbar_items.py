from __future__ import unicode_literals
import vmraid
from vmraid.utils.install import add_standard_navbar_items

def execute():
	# Add standard navbar items for ERPAdda in Navbar Settings
	vmraid.reload_doc('core', 'doctype', 'navbar_settings')
	vmraid.reload_doc('core', 'doctype', 'navbar_item')
	add_standard_navbar_items()