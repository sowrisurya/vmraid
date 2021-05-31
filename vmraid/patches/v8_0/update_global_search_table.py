from __future__ import unicode_literals
import vmraid

def execute():
	if not 'published' in vmraid.db.get_db_table_columns('__global_search'):
		vmraid.db.sql('''alter table __global_search
			add column `title` varchar(140)''')

		vmraid.db.sql('''alter table __global_search
			add column `route` varchar(140)''')

		vmraid.db.sql('''alter table __global_search
			add column `published` int(1) not null default 0''')
