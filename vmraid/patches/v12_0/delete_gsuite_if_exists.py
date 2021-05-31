import vmraid

def execute():
	'''
		Remove GSuite Template and GSuite Settings
	'''
	vmraid.delete_doc_if_exists("DocType", "GSuite Settings")
	vmraid.delete_doc_if_exists("DocType", "GSuite Templates")