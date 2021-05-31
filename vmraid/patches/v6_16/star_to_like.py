from __future__ import unicode_literals
import vmraid
from vmraid.database.schema import add_column

def execute():
	vmraid.db.sql("""update `tabSingles` set field='_liked_by' where field='_starred_by'""")
	vmraid.db.commit()

	for table in vmraid.db.get_tables():
		columns = [r[0] for r in vmraid.db.sql("DESC `{0}`".format(table))]
		if "_starred_by" in columns and '_liked_by' not in columns:
			vmraid.db.sql_ddl("""alter table `{0}` change `_starred_by` `_liked_by` Text """.format(table))

	if not vmraid.db.has_column("Communication", "_liked_by"):
		add_column("Communication", "_liked_by", "Text")
