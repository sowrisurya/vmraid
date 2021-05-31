from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc("core", "doctype", "communication")
	vmraid.db.sql("""update tabCommunication set reference_doctype = parenttype, reference_name = parent""")
