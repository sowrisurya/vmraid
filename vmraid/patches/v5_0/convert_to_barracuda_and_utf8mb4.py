from __future__ import unicode_literals
import vmraid
from vmraid.database.mariadb.setup_db import check_database_settings
from vmraid.model.meta import trim_tables

def execute():
	check_database_settings()

	for table in vmraid.db.get_tables():
		vmraid.db.sql_ddl("""alter table `{0}` ENGINE=InnoDB ROW_FORMAT=COMPRESSED""".format(table))
		try:
			vmraid.db.sql_ddl("""alter table `{0}` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci""".format(table))
		except:
			# if row size gets too large, let it be old charset!
			pass

