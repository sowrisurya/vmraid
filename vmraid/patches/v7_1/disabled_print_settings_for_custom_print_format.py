# -*- coding: utf-8 -*-
# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doctype('Print Format')
	vmraid.db.sql(""" 
		update 
			`tabPrint Format` 
		set 
			align_labels_right = 0, line_breaks = 0, show_section_headings = 0 
		where 
			custom_format = 1
		""")
