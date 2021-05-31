from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.db.sql("""update tabDocType set document_type='Document'
		where document_type='Transaction'""")
	vmraid.db.sql("""update tabDocType set document_type='Setup'
		where document_type='Master'""")		
