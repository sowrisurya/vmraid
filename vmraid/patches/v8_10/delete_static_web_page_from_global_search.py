from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.db.sql("""delete from `__global_search` where doctype='Static Web Page'""");