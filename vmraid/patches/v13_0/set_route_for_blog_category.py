import vmraid

def execute():
	categories = vmraid.get_list("Blog Category")
	for category in categories:
		doc = vmraid.get_doc("Blog Category", category["name"])
		doc.set_route()
		doc.save()
