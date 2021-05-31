# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals, print_function

import vmraid
import os
from vmraid.utils import get_files_path
from vmraid.core.doctype.file.file import get_content_hash


def execute():
	vmraid.reload_doc('core', 'doctype', 'file_data')
	for name, file_name, file_url in vmraid.db.sql(
			"""select name, file_name, file_url from `tabFile`
			where file_name is not null"""):
		b = vmraid.get_doc('File', name)
		old_file_name = b.file_name
		b.file_name = os.path.basename(old_file_name)
		if old_file_name.startswith('files/') or old_file_name.startswith('/files/'):
			b.file_url = os.path.normpath('/' + old_file_name)
		else:
			b.file_url = os.path.normpath('/files/' + old_file_name)
		try:
			_file = vmraid.get_doc("File", {"file_name": name})
			content = _file.get_content()
			b.content_hash = get_content_hash(content)
		except IOError:
			print('Warning: Error processing ', name)
			_file_name = old_file_name
			b.content_hash = None

		try:
			b.save()
		except vmraid.DuplicateEntryError:
			vmraid.delete_doc(b.doctype, b.name)

