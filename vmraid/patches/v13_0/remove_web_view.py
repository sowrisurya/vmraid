import vmraid

def execute():
	vmraid.delete_doc_if_exists("DocType", "Web View")
	vmraid.delete_doc_if_exists("DocType", "Web View Component")
	vmraid.delete_doc_if_exists("DocType", "CSS Class")