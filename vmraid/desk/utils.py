# Copyright (c) 2020, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import vmraid

def validate_route_conflict(doctype, name):
	'''
	Raises exception if name clashes with routes from other documents for /app routing
	'''

	all_names = []
	for _doctype in ['Page', 'Workspace', 'DocType']:
		try:
			all_names.extend([slug(d) for d in vmraid.get_all(_doctype, pluck='name') if (doctype != _doctype and d != name)])
		except vmraid.db.TableMissingError:
			pass

	if slug(name) in all_names:
		vmraid.msgprint(vmraid._('Name already taken, please set a new name'))
		raise vmraid.NameError

def slug(name):
	return name.lower().replace(' ', '-')