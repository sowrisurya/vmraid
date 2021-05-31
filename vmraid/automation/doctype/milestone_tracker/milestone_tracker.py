# -*- coding: utf-8 -*-
# Copyright (c) 2019, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import vmraid
from vmraid.model.document import Document
import vmraid.cache_manager
from vmraid.model import log_types

class MilestoneTracker(Document):
	def on_update(self):
		vmraid.cache_manager.clear_doctype_map('Milestone Tracker', self.document_type)

	def on_trash(self):
		vmraid.cache_manager.clear_doctype_map('Milestone Tracker', self.document_type)

	def apply(self, doc):
		before_save = doc.get_doc_before_save()
		from_value = before_save and before_save.get(self.track_field) or None
		if from_value != doc.get(self.track_field):
			vmraid.get_doc(dict(
				doctype = 'Milestone',
				reference_type = doc.doctype,
				reference_name = doc.name,
				track_field = self.track_field,
				from_value = from_value,
				value = doc.get(self.track_field),
				milestone_tracker = self.name,
			)).insert(ignore_permissions=True)

def evaluate_milestone(doc, event):
	if (vmraid.flags.in_install
		or vmraid.flags.in_migrate
		or vmraid.flags.in_setup_wizard
		or doc.doctype in log_types):
		return

	# track milestones related to this doctype
	for d in get_milestone_trackers(doc.doctype):
		vmraid.get_doc('Milestone Tracker', d.get('name')).apply(doc)

def get_milestone_trackers(doctype):
	return vmraid.cache_manager.get_doctype_map('Milestone Tracker', doctype,
		dict(document_type = doctype, disabled=0))

