# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.model.utils.rename_field import rename_field
from vmraid.modules import scrub, get_doctype_module

rename_map = {
	"Customize Form": [
		["customize_form_fields", "fields"]
	],
	"Email Alert": [
		["email_alert_recipients", "recipients"]
	],
	"Workflow": [
		["workflow_document_states", "states"],
		["workflow_transitions", "transitions"]
	]
}

def execute():
	vmraid.reload_doc("custom", "doctype", "customize_form")
	vmraid.reload_doc("email", "doctype", "notification")
	vmraid.reload_doc("desk", "doctype", "event")
	vmraid.reload_doc("workflow", "doctype", "workflow")

	for dt, field_list in rename_map.items():
		for field in field_list:
			rename_field(dt, field[0], field[1])
