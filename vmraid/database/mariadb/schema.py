from __future__ import unicode_literals

import vmraid
from vmraid import _
from vmraid.database.schema import DBTable

class MariaDBTable(DBTable):
	def create(self):
		add_text = ''

		# columns
		column_defs = self.get_column_definitions()
		if column_defs: add_text += ',\n'.join(column_defs) + ',\n'

		# index
		index_defs = self.get_index_definitions()
		if index_defs: add_text += ',\n'.join(index_defs) + ',\n'

		# create table
		vmraid.db.sql("""create table `%s` (
			name varchar({varchar_len}) not null primary key,
			creation datetime(6),
			modified datetime(6),
			modified_by varchar({varchar_len}),
			owner varchar({varchar_len}),
			docstatus int(1) not null default '0',
			parent varchar({varchar_len}),
			parentfield varchar({varchar_len}),
			parenttype varchar({varchar_len}),
			idx int(8) not null default '0',
			%sindex parent(parent),
			index modified(modified))
			ENGINE={engine}
			ROW_FORMAT=COMPRESSED
			CHARACTER SET=utf8mb4
			COLLATE=utf8mb4_unicode_ci""".format(varchar_len=vmraid.db.VARCHAR_LEN,
				engine=self.meta.get("engine") or 'InnoDB') % (self.table_name, add_text))

	def alter(self):
		for col in self.columns.values():
			col.build_for_alter_table(self.current_columns.get(col.fieldname.lower()))

		add_column_query = []
		modify_column_query = []
		add_index_query = []
		drop_index_query = []

		columns_to_modify =  set(self.change_type + self.add_unique + self.set_default)

		for col in self.add_column:
			add_column_query.append("ADD COLUMN `{}` {}".format(col.fieldname, col.get_definition()))

		for col in columns_to_modify:
			modify_column_query.append("MODIFY `{}` {}".format(col.fieldname, col.get_definition()))

		for col in self.add_index:
			# if index key not exists
			if not vmraid.db.sql("SHOW INDEX FROM `%s` WHERE key_name = %s" %
					(self.table_name, '%s'), col.fieldname):
				add_index_query.append("ADD INDEX `{}`(`{}`)".format(col.fieldname, col.fieldname))

		for col in self.drop_index:
			if col.fieldname != 'name': # primary key
				# if index key exists
				if vmraid.db.sql("""SHOW INDEX FROM `{0}`
					WHERE key_name=%s
					AND Non_unique=%s""".format(self.table_name), (col.fieldname, col.unique)):
					drop_index_query.append("drop index `{}`".format(col.fieldname))

		try:
			for query_parts in [add_column_query, modify_column_query, add_index_query, drop_index_query]:
				if query_parts:
					query_body = ", ".join(query_parts)
					query = "ALTER TABLE `{}` {}".format(self.table_name, query_body)
					vmraid.db.sql(query)

		except Exception as e:
			# sanitize
			if e.args[0]==1060:
				vmraid.throw(str(e))
			elif e.args[0]==1062:
				fieldname = str(e).split("'")[-2]
				vmraid.throw(_("{0} field cannot be set as unique in {1}, as there are non-unique existing values").format(
					fieldname, self.table_name))
			elif e.args[0]==1067:
				vmraid.throw(str(e.args[1]))
			else:
				raise e
