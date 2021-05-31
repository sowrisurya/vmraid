from __future__ import unicode_literals
import vmraid
from vmraid.utils.password import create_auth_table, set_encrypted_password

def execute():
	if '__OldAuth' not in vmraid.db.get_tables():
		vmraid.db.sql_ddl('''alter table `__Auth` rename `__OldAuth`''')

	create_auth_table()

	# user passwords
	vmraid.db.sql('''insert ignore into `__Auth` (doctype, name, fieldname, `password`)
		(select 'User', `name`, 'password', `password` from `__OldAuth`)''')

	vmraid.db.commit()

	# other password fields
	for doctype in vmraid.db.sql_list('''select distinct parent from `tabDocField`
		where fieldtype="Password" and parent != "User"'''):

		vmraid.reload_doctype(doctype)
		meta = vmraid.get_meta(doctype)

		for df in meta.get('fields', {'fieldtype': 'Password'}):
			if meta.issingle:
				password = vmraid.db.get_value(doctype, doctype, df.fieldname)
				if password:
					set_encrypted_password(doctype, doctype, password, fieldname=df.fieldname)
					vmraid.db.set_value(doctype, doctype, df.fieldname, '*'*len(password))

			else:
				for d in vmraid.db.sql('''select name, `{fieldname}` from `tab{doctype}`
					where `{fieldname}` is not null'''.format(fieldname=df.fieldname, doctype=doctype), as_dict=True):

					set_encrypted_password(doctype, d.name, d.get(df.fieldname), fieldname=df.fieldname)

				vmraid.db.sql('''update `tab{doctype}` set `{fieldname}`=repeat("*", char_length(`{fieldname}`))'''
					.format(doctype=doctype, fieldname=df.fieldname))

			vmraid.db.commit()

	vmraid.db.sql_ddl('''drop table `__OldAuth`''')
