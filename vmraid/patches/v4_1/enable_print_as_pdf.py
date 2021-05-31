# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc("core", "doctype", "print_settings")
	print_settings = vmraid.get_doc("Print Settings")
	print_settings.print_style = "Modern"

	try:
		import pdfkit
	except ImportError:
		pass
	else:
		# if someone has already configured in Outgoing Email Settings
		outgoing_email_settings = vmraid.db.get_singles_dict("Outgoing Email Settings")
		if "send_print_as_pdf" in outgoing_email_settings:
			print_settings.send_print_as_pdf = outgoing_email_settings.send_print_as_pdf
			print_settings.pdf_page_size = outgoing_email_settings.pdf_page_size

		else:
			print_settings.send_print_as_pdf = 1

	print_settings.save()
