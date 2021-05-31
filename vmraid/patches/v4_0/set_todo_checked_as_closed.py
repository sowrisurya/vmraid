from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc("core", "doctype", "todo")
	try:
		vmraid.db.sql("""update tabToDo set status = if(ifnull(checked,0)=0, 'Open', 'Closed')""")
	except:
		pass
