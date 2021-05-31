import vmraid

def execute():
	providers = vmraid.get_all("Social Login Key")

	for provider in providers:
		doc = vmraid.get_doc("Social Login Key", provider)
		doc.set_icon()
		doc.save()