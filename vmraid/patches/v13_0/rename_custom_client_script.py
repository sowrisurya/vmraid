import vmraid


def execute():
	if vmraid.db.exists("DocType", "Client Script"):
		return

	vmraid.rename_doc("DocType", "Custom Script", "Client Script")
	vmraid.reload_doctype("Client Script", force=True)
