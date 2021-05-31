# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# License: See license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.model.document import Document

class Note(Document):
	def autoname(self):
		# replace forbidden characters
		import re
		self.name = re.sub("[%'\"#*?`]", "", self.title.strip())

	def validate(self):
		if self.notify_on_login and not self.expire_notification_on:

			# expire this notification in a week (default)
			self.expire_notification_on = vmraid.utils.add_days(self.creation, 7)

	def before_print(self, settings=None):
		self.print_heading = self.name
		self.sub_heading = ""

@vmraid.whitelist()
def mark_as_seen(note):
	note = vmraid.get_doc('Note', note)
	if vmraid.session.user not in [d.user for d in note.seen_by]:
		note.append('seen_by', {'user': vmraid.session.user})
		note.save(ignore_version=True)

def get_permission_query_conditions(user):
	if not user: user = vmraid.session.user

	if user == "Administrator":
		return ""

	return """(`tabNote`.public=1 or `tabNote`.owner="{user}")""".format(user=user)

def has_permission(doc, ptype, user):
	if doc.public == 1 or user == "Administrator":
		return True

	if user == doc.owner:
		return True

	return False
