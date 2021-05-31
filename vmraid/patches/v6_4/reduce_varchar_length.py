from __future__ import unicode_literals, print_function
import vmraid

def execute():
	for doctype in vmraid.get_all("DocType", filters={"issingle": 0}):
		doctype = doctype.name
		if not vmraid.db.table_exists(doctype):
			continue

		for column in vmraid.db.sql("desc `tab{doctype}`".format(doctype=doctype), as_dict=True):
			fieldname = column["Field"]
			column_type = column["Type"]

			if not column_type.startswith("varchar"):
				continue

			max_length = vmraid.db.sql("""select max(char_length(`{fieldname}`)) from `tab{doctype}`"""\
				.format(fieldname=fieldname, doctype=doctype))

			max_length = max_length[0][0] if max_length else None

			if max_length and 140 < max_length <= 255:
				print(
					"setting length of '{fieldname}' in '{doctype}' as {length}".format(
					fieldname=fieldname, doctype=doctype, length=max_length)
				)

				# create property setter for length
				vmraid.make_property_setter({
					"doctype": doctype,
					"fieldname": fieldname,
					"property": "length",
					"value": max_length,
					"property_type": "Int"
				})

		vmraid.clear_cache(doctype=doctype)
