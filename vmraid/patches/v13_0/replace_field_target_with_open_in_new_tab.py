import vmraid


def execute():
	doctype = "Top Bar Item"
	if not vmraid.db.table_exists(doctype) \
			or not vmraid.db.has_column(doctype, "target"):
		return

	vmraid.reload_doc("website", "doctype", "top_bar_item")
	vmraid.db.set_value(doctype, {"target": 'target = "_blank"'}, 'open_in_new_tab', 1)
