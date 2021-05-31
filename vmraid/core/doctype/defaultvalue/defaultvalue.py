# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid

from vmraid.model.document import Document

class DefaultValue(Document):
	pass

def on_doctype_update():
	"""Create indexes for `tabDefaultValue` on `(parent, defkey)`"""
	vmraid.db.commit()
	vmraid.db.add_index(doctype='DefaultValue',
		fields=['parent', 'defkey'],
		index_name='defaultvalue_parent_defkey_index')

	vmraid.db.add_index(doctype='DefaultValue',
		fields=['parent', 'parenttype'],
		index_name='defaultvalue_parent_parenttype_index')
