from __future__ import unicode_literals
import vmraid

def execute():
	for name in vmraid.db.sql_list("""select name from `tabToDo`
		where ifnull(reference_type, '')!='' and ifnull(reference_name, '')!=''"""):
		try:
			vmraid.get_doc("ToDo", name).on_update()
		except Exception as e:
			if not vmraid.db.is_table_missing(e):
				raise
