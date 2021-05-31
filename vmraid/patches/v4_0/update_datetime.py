from __future__ import unicode_literals
import vmraid

def execute():
	for table in vmraid.db.sql_list("show tables"):
		for field in vmraid.db.sql("desc `%s`" % table):
			if field[1]=="datetime":
				vmraid.db.sql("alter table `%s` change `%s` `%s` datetime(6)" % \
					 (table, field[0], field[0]))
			elif field[1]=="time":
				vmraid.db.sql("alter table `%s` change `%s` `%s` time(6)" % \
					 (table, field[0], field[0]))
