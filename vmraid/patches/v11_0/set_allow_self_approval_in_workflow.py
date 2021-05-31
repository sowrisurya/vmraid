from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc("workflow", "doctype", "workflow_transition")
	vmraid.db.sql("update `tabWorkflow Transition` set allow_self_approval=1")