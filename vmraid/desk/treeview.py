# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid
from vmraid import _

@vmraid.whitelist()
def get_all_nodes(doctype, label, parent, tree_method, **filters):
	'''Recursively gets all data from tree nodes'''

	if 'cmd' in filters:
		del filters['cmd']
	filters.pop('data', None)

	tree_method = vmraid.get_attr(tree_method)

	if not tree_method in vmraid.whitelisted:
		vmraid.throw(_("Not Permitted"), vmraid.PermissionError)

	data = tree_method(doctype, parent, **filters)
	out = [dict(parent=label, data=data)]

	if 'is_root' in filters:
		del filters['is_root']
	to_check = [d.get('value') for d in data if d.get('expandable')]

	while to_check:
		parent = to_check.pop()
		data = tree_method(doctype, parent, is_root=False, **filters)
		out.append(dict(parent=parent, data=data))
		for d in data:
			if d.get('expandable'):
				to_check.append(d.get('value'))

	return out

@vmraid.whitelist()
def get_children(doctype, parent='', **filters):
	return _get_children(doctype, parent)

def _get_children(doctype, parent='', ignore_permissions=False):
	parent_field = 'parent_' + doctype.lower().replace(' ', '_')
	filters = [['ifnull(`{0}`,"")'.format(parent_field), '=', parent],
		['docstatus', '<' ,'2']]

	meta = vmraid.get_meta(doctype)

	return vmraid.get_list(
		doctype,
		fields=[
			'name as value',
			'{0} as title'.format(meta.get('title_field') or 'name'),
			'is_group as expandable'
		],
		filters=filters,
		order_by='name',
		ignore_permissions=ignore_permissions
	)

@vmraid.whitelist()
def add_node():
	args = make_tree_args(**vmraid.form_dict)
	doc = vmraid.get_doc(args)

	doc.save()

def make_tree_args(**kwarg):
	kwarg.pop('cmd', None)

	doctype = kwarg['doctype']
	parent_field = 'parent_' + doctype.lower().replace(' ', '_')
	name_field = kwarg.get('name_field', doctype.lower().replace(' ', '_') + '_name')

	if kwarg['is_root'] == 'false': kwarg['is_root'] = False
	if kwarg['is_root'] == 'true': kwarg['is_root'] = True

	kwarg.update({
		name_field: kwarg[name_field],
		parent_field: kwarg.get("parent") or kwarg.get(parent_field)
	})

	return vmraid._dict(kwarg)
