from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.delete_doc("DocType", "Post")
	vmraid.delete_doc("DocType", "Website Group")
	vmraid.delete_doc("DocType", "Website Route Permission")
	vmraid.delete_doc("DocType", "User Vote")
	vmraid.delete_doc("DocType", "Notification Count")
