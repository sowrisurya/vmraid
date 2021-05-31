from __future__ import unicode_literals
import vmraid

def execute():
	for t in vmraid.db.sql('show table status'):
		if t[0].startswith('tab'):
			vmraid.db.sql('update tabDocType set engine=%s where name=%s', (t[1], t[0][3:]))