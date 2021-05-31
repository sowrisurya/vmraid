# -*- coding: utf-8 -*-
# Copyright (c) 2019, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals, absolute_import
import vmraid
from vmraid import _
import json
from vmraid.model.document import Document
from vmraid.core.doctype.user.user import extract_mentions
from vmraid.desk.doctype.notification_log.notification_log import enqueue_create_notification,\
	get_title, get_title_html
from vmraid.utils import get_fullname
from vmraid.website.render import clear_cache
from vmraid.database.schema import add_column
from vmraid.exceptions import ImplicitCommitError

class Comment(Document):
	def after_insert(self):
		self.notify_mentions()
		self.notify_change('add')

	def validate(self):
		if not self.comment_email:
			self.comment_email = vmraid.session.user
		self.content = vmraid.utils.sanitize_html(self.content)

	def on_update(self):
		update_comment_in_doc(self)
		if self.is_new():
			self.notify_change('update')

	def on_trash(self):
		self.remove_comment_from_cache()
		self.notify_change('delete')

	def notify_change(self, action):
		key_map = {
			'Like': 'like_logs',
			'Assigned': 'assignment_logs',
			'Assignment Completed': 'assignment_logs',
			'Comment': 'comments',
			'Attachment': 'attachment_logs',
			'Attachment Removed': 'attachment_logs',
		}
		key = key_map.get(self.comment_type)
		if not key: return

		vmraid.publish_realtime('update_docinfo_for_{}_{}'.format(self.reference_doctype, self.reference_name), {
			'doc': self.as_dict(),
			'key': key,
			'action': action
		}, after_commit=True)

	def remove_comment_from_cache(self):
		_comments = get_comments_from_parent(self)
		for c in _comments:
			if c.get("name")==self.name:
				_comments.remove(c)

		update_comments_in_parent(self.reference_doctype, self.reference_name, _comments)

	def notify_mentions(self):
		if self.reference_doctype and self.reference_name and self.content:
			mentions = extract_mentions(self.content)

			if not mentions:
				return

			sender_fullname = get_fullname(vmraid.session.user)
			title = get_title(self.reference_doctype, self.reference_name)

			recipients = [vmraid.db.get_value("User", {"enabled": 1, "name": name, "user_type": "System User", "allowed_in_mentions": 1}, "email")
				for name in mentions]

			notification_message = _('''{0} mentioned you in a comment in {1} {2}''')\
				.format(vmraid.bold(sender_fullname), vmraid.bold(self.reference_doctype), get_title_html(title))

			notification_doc = {
				'type': 'Mention',
				'document_type': self.reference_doctype,
				'document_name': self.reference_name,
				'subject': notification_message,
				'from_user': vmraid.session.user,
				'email_content': self.content
			}

			enqueue_create_notification(recipients, notification_doc)


def on_doctype_update():
	vmraid.db.add_index("Comment", ["reference_doctype", "reference_name"])
	vmraid.db.add_index("Comment", ["link_doctype", "link_name"])


def update_comment_in_doc(doc):
	"""Updates `_comments` (JSON) property in parent Document.
	Creates a column `_comments` if property does not exist.

	Only user created Communication or Comment of type Comment are saved.

	`_comments` format

		{
			"comment": [String],
			"by": [user],
			"name": [Comment Document name]
		}"""

	# only comments get updates, not likes, assignments etc.
	if doc.doctype == 'Comment' and doc.comment_type != 'Comment':
		return

	def get_truncated(content):
		return (content[:97] + '...') if len(content) > 100 else content

	if doc.reference_doctype and doc.reference_name and doc.content:
		_comments = get_comments_from_parent(doc)

		updated = False
		for c in _comments:
			if c.get("name")==doc.name:
				c["comment"] = get_truncated(doc.content)
				updated = True

		if not updated:
			_comments.append({
				"comment": get_truncated(doc.content),

				# "comment_email" for Comment and "sender" for Communication
				"by": getattr(doc, 'comment_email', None) or getattr(doc, 'sender', None) or doc.owner,
				"name": doc.name
			})

		update_comments_in_parent(doc.reference_doctype, doc.reference_name, _comments)


def get_comments_from_parent(doc):
	'''
	get the list of comments cached in the document record in the column
	`_comments`
	'''
	try:
		_comments = vmraid.db.get_value(doc.reference_doctype, doc.reference_name, "_comments") or "[]"

	except Exception as e:
		if vmraid.db.is_missing_table_or_column(e):
			_comments = "[]"

		else:
			raise

	try:
		return json.loads(_comments)
	except ValueError:
		return []

def update_comments_in_parent(reference_doctype, reference_name, _comments):
	"""Updates `_comments` property in parent Document with given dict.

	:param _comments: Dict of comments."""
	if not reference_doctype or not reference_name or vmraid.db.get_value("DocType", reference_doctype, "issingle") or vmraid.db.get_value("DocType", reference_doctype, "is_virtual"):
		return

	try:
		# use sql, so that we do not mess with the timestamp
		vmraid.db.sql("""update `tab{0}` set `_comments`=%s where name=%s""".format(reference_doctype), # nosec
			(json.dumps(_comments[-100:]), reference_name))

	except Exception as e:
		if vmraid.db.is_column_missing(e) and getattr(vmraid.local, 'request', None):
			# missing column and in request, add column and update after commit
			vmraid.local._comments = (getattr(vmraid.local, "_comments", [])
				+ [(reference_doctype, reference_name, _comments)])

		elif vmraid.db.is_data_too_long(e):
			raise vmraid.DataTooLongException

		else:
			raise ImplicitCommitError

	else:
		if not vmraid.flags.in_patch:
			reference_doc = vmraid.get_doc(reference_doctype, reference_name)
			if getattr(reference_doc, "route", None):
				clear_cache(reference_doc.route)

def update_comments_in_parent_after_request():
	"""update _comments in parent if _comments column is missing"""
	if hasattr(vmraid.local, "_comments"):
		for (reference_doctype, reference_name, _comments) in vmraid.local._comments:
			add_column(reference_doctype, "_comments", "Text")
			update_comments_in_parent(reference_doctype, reference_name, _comments)

		vmraid.db.commit()
