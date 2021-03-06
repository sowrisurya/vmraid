# -*- coding: utf-8 -*-
# Copyright (c) 2017, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.modules import get_module_path, scrub_dt_dn
from vmraid.modules.export_file import export_to_files, create_init_py
from vmraid.custom.doctype.custom_field.custom_field import create_custom_field
from vmraid.model.document import Document

class DataMigrationPlan(Document):
	def on_update(self):
		# update custom fields in mappings
		self.make_custom_fields_for_mappings()

		if vmraid.flags.in_import or vmraid.flags.in_test:
			return

		if vmraid.local.conf.get('developer_mode'):
			record_list =[['Data Migration Plan', self.name]]

			for m in self.mappings:
				record_list.append(['Data Migration Mapping', m.mapping])

			export_to_files(record_list=record_list, record_module=self.module)

			for m in self.mappings:
				dt, dn = scrub_dt_dn('Data Migration Mapping', m.mapping)
				create_init_py(get_module_path(self.module), dt, dn)

	def make_custom_fields_for_mappings(self):
		vmraid.flags.ignore_in_install = True
		label = self.name + ' ID'
		fieldname = vmraid.scrub(label)

		df = {
			'label': label,
			'fieldname': fieldname,
			'fieldtype': 'Data',
			'hidden': 1,
			'read_only': 1,
			'unique': 1,
			'no_copy': 1
		}

		for m in self.mappings:
			mapping = vmraid.get_doc('Data Migration Mapping', m.mapping)
			create_custom_field(mapping.local_doctype, df)
			mapping.migration_id_field = fieldname
			mapping.save()

		# Create custom field in Deleted Document
		create_custom_field('Deleted Document', df)
		vmraid.flags.ignore_in_install = False

	def pre_process_doc(self, mapping_name, doc):
		module = self.get_mapping_module(mapping_name)

		if module and hasattr(module, 'pre_process'):
			return module.pre_process(doc)
		return doc

	def post_process_doc(self, mapping_name, local_doc=None, remote_doc=None):
		module = self.get_mapping_module(mapping_name)

		if module and hasattr(module, 'post_process'):
			return module.post_process(local_doc=local_doc, remote_doc=remote_doc)

	def get_mapping_module(self, mapping_name):
		try:
			module_def = vmraid.get_doc("Module Def", self.module)
			module = vmraid.get_module('{app}.{module}.data_migration_mapping.{mapping_name}'.format(
				app= module_def.app_name,
				module=vmraid.scrub(self.module),
				mapping_name=vmraid.scrub(mapping_name)
			))
			return module
		except ImportError:
			return None
