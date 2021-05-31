from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc('core', 'doctype', 'user_permission')
	vmraid.delete_doc('core', 'page', 'user-permissions')
	for perm in vmraid.db.sql("""
		select
			name, parent, defkey, defvalue
		from
			tabDefaultValue
		where
			parent not in ('__default', '__global')
		and
			substr(defkey,1,1)!='_'
		and
			parenttype='User Permission'
		""", as_dict=True):
		if vmraid.db.exists(perm.defkey, perm.defvalue) and vmraid.db.exists('User', perm.parent):
			vmraid.get_doc(dict(
				doctype='User Permission',
				user=perm.parent,
				allow=perm.defkey,
				for_value=perm.defvalue,
				apply_for_all_roles=0,
			)).insert(ignore_permissions = True)

	vmraid.db.sql('delete from tabDefaultValue where parenttype="User Permission"')
