import vmraid

def execute():
	vmraid.delete_doc_if_exists("DocType", "Tag Category")
	vmraid.delete_doc_if_exists("DocType", "Tag Doc Category")

	vmraid.reload_doc("desk", "doctype", "tag")
	vmraid.reload_doc("desk", "doctype", "tag_link")

	tag_list = []
	tag_links = []
	time = vmraid.utils.get_datetime()

	for doctype in vmraid.get_list("DocType", filters={"istable": 0, "issingle": 0}):
		if not vmraid.db.count(doctype.name) or not vmraid.db.has_column(doctype.name, "_user_tags"):
			continue

		for _user_tags in vmraid.db.sql("select `name`, `_user_tags` from `tab{0}`".format(doctype.name), as_dict=True):
			if not _user_tags.get("_user_tags"):
				continue

			for tag in _user_tags.get("_user_tags").split(",") if _user_tags.get("_user_tags") else []:
				if not tag:
					continue

				tag_list.append((tag.strip(), time, time, 'Administrator'))

				tag_link_name = vmraid.generate_hash(_user_tags.name + tag.strip() + doctype.name, 10)
				tag_links.append((tag_link_name, doctype.name, _user_tags.name, tag.strip(), time, time, 'Administrator'))


	vmraid.db.bulk_insert("Tag", fields=["name", "creation", "modified", "modified_by"], values=set(tag_list), ignore_duplicates=True)
	vmraid.db.bulk_insert("Tag Link", fields=["name", "document_type", "document_name", "tag", "creation", "modified", "modified_by"], values=set(tag_links), ignore_duplicates=True)
