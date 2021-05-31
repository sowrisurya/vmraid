# -*- coding: utf-8 -*-
# Copyright (c) 2019, VMRaid Technologies and contributors
# For license information, please see license.txt

# imports - standard imports
from __future__ import unicode_literals

# imports - module imports
import vmraid
from vmraid.model.document import Document


class AccessLog(Document):
	pass


@vmraid.whitelist()
def make_access_log(doctype=None, document=None, method=None, file_type=None,
		report_name=None, filters=None, page=None, columns=None):

	user = vmraid.session.user

	doc = vmraid.get_doc({
		'doctype': 'Access Log',
		'user': user,
		'export_from': doctype,
		'reference_document': document,
		'file_type': file_type,
		'report_name': report_name,
		'page': page,
		'method': method,
		'filters': vmraid.utils.cstr(filters) if filters else None,
		'columns': columns
	})
	doc.insert(ignore_permissions=True)

	# `vmraid.db.commit` added because insert doesnt `commit` when called in GET requests like `printview`
	vmraid.db.commit()
