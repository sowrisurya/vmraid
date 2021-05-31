# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	for d in vmraid.db.sql("""select name, dt, insert_after from `tabCustom Field`
		where docstatus < 2""", as_dict=1):
			dt_meta = vmraid.get_meta(d.dt)
			if not dt_meta.get_field(d.insert_after):
				cf = vmraid.get_doc("Custom Field", d.name)
				df = dt_meta.get("fields", {"label": d.insert_after})
				if df:
					cf.insert_after = df[0].fieldname
				else:
					cf.insert_after = None
				cf.save()
