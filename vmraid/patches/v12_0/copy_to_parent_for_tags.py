import vmraid

def execute():

	vmraid.db.sql("UPDATE `tabTag Link` SET parenttype=document_type")
	vmraid.db.sql("UPDATE `tabTag Link` SET parent=document_name")