import unittest
import vmraid

from vmraid.utils import cstr
from vmraid.core.utils import find
from vmraid.custom.doctype.property_setter.property_setter import make_property_setter


class TestDBUpdate(unittest.TestCase):
	def test_db_update(self):
		doctype = 'User'
		vmraid.reload_doctype('User', force=True)
		vmraid.model.meta.trim_tables('User')
		make_property_setter(doctype, 'bio', 'fieldtype', 'Text', 'Data')
		make_property_setter(doctype, 'middle_name', 'fieldtype', 'Data', 'Text')
		make_property_setter(doctype, 'enabled', 'default', '1', 'Int')

		vmraid.db.updatedb(doctype)

		field_defs = get_field_defs(doctype)
		table_columns = vmraid.db.get_table_columns_description('tab{}'.format(doctype))

		self.assertEqual(len(field_defs), len(table_columns))

		for field_def in field_defs:
			fieldname = field_def.get('fieldname')
			table_column = find(table_columns, lambda d: d.get('name') == fieldname)

			fieldtype = get_fieldtype_from_def(field_def)

			fallback_default = '0' if field_def.get('fieldtype') in vmraid.model.numeric_fieldtypes else 'NULL'
			default = field_def.default if field_def.default is not None else fallback_default

			self.assertEqual(fieldtype, table_column.type)
			self.assertIn(cstr(table_column.default) or 'NULL', [cstr(default), "'{}'".format(default)])

def get_fieldtype_from_def(field_def):
	fieldtuple = vmraid.db.type_map.get(field_def.fieldtype, ('', 0))
	fieldtype = fieldtuple[0]
	if fieldtype in ('varchar', 'datetime', 'int'):
		fieldtype += '({})'.format(field_def.length or fieldtuple[1])
	return fieldtype

def get_field_defs(doctype):
	meta = vmraid.get_meta(doctype, cached=False)
	field_defs = meta.get_fieldnames_with_value(True)
	field_defs += get_other_fields_meta(meta)
	return field_defs

def get_other_fields_meta(meta):
	default_fields_map = {
		'name': ('Data', 0),
		'owner': ('Data', 0),
		'parent': ('Data', 0),
		'parentfield': ('Data', 0),
		'modified_by': ('Data', 0),
		'parenttype': ('Data', 0),
		'creation': ('Datetime', 0),
		'modified': ('Datetime', 0),
		'idx': ('Int', 8),
		'docstatus': ('Check', 0)
	}

	optional_fields = vmraid.db.OPTIONAL_COLUMNS
	if meta.track_seen:
		optional_fields.append('_seen')

	optional_fields_map = {field: ('Text', 0) for field in optional_fields}
	fields = dict(default_fields_map, **optional_fields_map)
	field_map =  [vmraid._dict({'fieldname': field, 'fieldtype': _type, 'length': _length}) for field, (_type, _length) in fields.items()]

	return field_map