from __future__ import unicode_literals
import vmraid
from vmraid.model.rename_doc import rename_doc


def execute():
	if vmraid.db.table_exists("Workflow Action") and not vmraid.db.table_exists("Workflow Action Master"):
		rename_doc('DocType', 'Workflow Action', 'Workflow Action Master')
		vmraid.reload_doc('workflow', 'doctype', 'workflow_action_master')
