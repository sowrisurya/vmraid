import vmraid
from ..role import desk_properties

def execute():
	vmraid.reload_doctype('role')
	for role in vmraid.get_all('Role', ['name', 'desk_access']):
		role_doc = vmraid.get_doc('Role', role.name)
		for key in desk_properties:
			role_doc.set(key, role_doc.desk_access)
		role_doc.save()