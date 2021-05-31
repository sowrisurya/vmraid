from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc("core", "doctype", "docperm")
	
	# delete same as cancel (map old permissions)
	vmraid.db.sql("""update tabDocPerm set `delete`=ifnull(`cancel`,0)""")
	
	# can't cancel if can't submit
	vmraid.db.sql("""update tabDocPerm set `cancel`=0 where ifnull(`submit`,0)=0""")
	
	vmraid.clear_cache()