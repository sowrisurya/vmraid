from __future__ import unicode_literals
import vmraid

def execute():
	if not 'tabError Log' in vmraid.db.get_tables():
		vmraid.rename_doc('DocType', 'Scheduler Log', 'Error Log')
		vmraid.db.sql("""delete from `tabError Log` where datediff(curdate(), creation) > 30""")
		vmraid.db.commit()
		vmraid.db.sql('alter table `tabError Log` change column name name varchar(140)')
		vmraid.db.sql('alter table `tabError Log` change column parent parent varchar(140)')
		vmraid.db.sql('alter table `tabError Log` engine=MyISAM')
