from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc('custom', 'doctype', 'custom_field', force=True)

	try:
		vmraid.db.sql('update `tabCustom Field` set in_standard_filter = in_filter_dash')
	except Exception as e:
		if not vmraid.db.is_missing_column(e): raise e

	for doctype in vmraid.get_all("DocType", {"istable": 0, "issingle": 0, "custom": 0}):
		try:
			vmraid.reload_doctype(doctype.name, force=True)
		except KeyError:
			pass
		except vmraid.db.DataError:
			pass
		except Exception:
			pass
