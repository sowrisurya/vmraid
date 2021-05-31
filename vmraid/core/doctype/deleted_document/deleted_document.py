# -*- coding: utf-8 -*-
# Copyright (c) 2015, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
import json
from vmraid.desk.doctype.bulk_update.bulk_update import show_progress
from vmraid.model.document import Document
from vmraid import _


class DeletedDocument(Document):
	pass


@vmraid.whitelist()
def restore(name, alert=True):
	deleted = vmraid.get_doc('Deleted Document', name)

	if deleted.restored:
		vmraid.throw(_("Document {0} Already Restored").format(name), exc=vmraid.DocumentAlreadyRestored)

	doc = vmraid.get_doc(json.loads(deleted.data))

	try:
		doc.insert()
	except vmraid.DocstatusTransitionError:
		vmraid.msgprint(_("Cancelled Document restored as Draft"))
		doc.docstatus = 0
		doc.insert()

	doc.add_comment('Edit', _('restored {0} as {1}').format(deleted.deleted_name, doc.name))

	deleted.new_name = doc.name
	deleted.restored = 1
	deleted.db_update()

	if alert:
		vmraid.msgprint(_('Document Restored'))


@vmraid.whitelist()
def bulk_restore(docnames):
	docnames = vmraid.parse_json(docnames)
	message = _('Restoring Deleted Document')
	restored, invalid, failed = [], [], []

	for i, d in enumerate(docnames):
		try:
			show_progress(docnames, message, i + 1, d)
			restore(d, alert=False)
			vmraid.db.commit()
			restored.append(d)

		except vmraid.DocumentAlreadyRestored:
			vmraid.message_log.pop()
			invalid.append(d)

		except Exception:
			vmraid.message_log.pop()
			failed.append(d)
			vmraid.db.rollback()

	return {
		"restored": restored,
		"invalid": invalid,
		"failed": failed
	}
