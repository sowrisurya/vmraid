# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import vmraid

def execute():
	# communication
	unwanted_indexes = ["communication_date_index", "message_id_index", "modified_index", 
		"creation_index", "reference_owner", "communication_date"]
		
	for k in unwanted_indexes:
		try:
			vmraid.db.sql("drop index {0} on `tabCommunication`".format(k))
		except:
			pass