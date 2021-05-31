# -*- coding: utf-8 -*-
# Copyright (c) 2018, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid import _
from vmraid.utils import cint

from vmraid.model.document import Document

class PrintSettings(Document):
	def on_update(self):
		vmraid.clear_cache()

	@vmraid.whitelist()
	def get_printers(self,ip="localhost",port=631):
		printer_list = []
		try:
			import cups
		except ImportError:
			vmraid.throw(_("You need to install pycups to use this feature!"))
			return
		try:
			cups.setServer(self.server_ip)
			cups.setPort(self.port)
			conn = cups.Connection()
			printers = conn.getPrinters()
			printer_list = printers.keys()
		except RuntimeError:
			vmraid.throw(_("Failed to connect to server"))
		except vmraid.ValidationError:
			vmraid.throw(_("Failed to connect to server"))
		return printer_list

@vmraid.whitelist()
def is_print_server_enabled():
	if not hasattr(vmraid.local, 'enable_print_server'):
		vmraid.local.enable_print_server = cint(vmraid.db.get_single_value('Print Settings',
			'enable_print_server'))

	return vmraid.local.enable_print_server
