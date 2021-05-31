from __future__ import unicode_literals
import vmraid
from vmraid.utils import cint
from vmraid.model import default_fields

def execute():
	for table in vmraid.db.get_tables():
		doctype = table[3:]
		if vmraid.db.exists("DocType", doctype):
			fieldnames = [df["fieldname"] for df in
				vmraid.get_all("DocField", fields=["fieldname"], filters={"parent": doctype})]
			custom_fieldnames = [df["fieldname"] for df in
				vmraid.get_all("Custom Field", fields=["fieldname"], filters={"dt": doctype})]

		else:
			fieldnames = custom_fieldnames = []

		for column in vmraid.db.sql("""desc `{0}`""".format(table), as_dict=True):
			if column["Type"]=="int(1)":
				fieldname = column["Field"]

				# only change for defined fields, ignore old fields that don't exist in meta
				if not (fieldname in default_fields or fieldname in fieldnames or fieldname in custom_fieldnames):
					continue

				# set 0
				vmraid.db.sql("""update `{table}` set `{column}`=0 where `{column}` is null"""\
					.format(table=table, column=fieldname))
				vmraid.db.commit()

				# change definition
				vmraid.db.sql_ddl("""alter table `{table}`
					modify `{column}` int(1) not null default {default}"""\
					.format(table=table, column=fieldname, default=cint(column["Default"])))
