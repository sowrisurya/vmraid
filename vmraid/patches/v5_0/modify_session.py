from __future__ import unicode_literals
import vmraid

def execute():
	if "device" not in vmraid.db.get_table_columns("Sessions"):
		vmraid.db.sql("alter table tabSessions add column `device` varchar(255) default 'desktop'")
