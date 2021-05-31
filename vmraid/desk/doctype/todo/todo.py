# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid
import json

from vmraid.model.document import Document
from vmraid.utils import get_fullname

exclude_from_linked_with = True

class ToDo(Document):
	def validate(self):
		self._assignment = None
		if self.is_new():

			if self.assigned_by == self.owner:
				assignment_message = vmraid._("{0} self assigned this task: {1}").format(get_fullname(self.assigned_by), self.description)
			else:
				assignment_message = vmraid._("{0} assigned {1}: {2}").format(get_fullname(self.assigned_by), get_fullname(self.owner), self.description)

			self._assignment = {
				"text": assignment_message,
				"comment_type": "Assigned"
			}

		else:
			# NOTE the previous value is only available in validate method
			if self.get_db_value("status") != self.status:
				self._assignment = {
					"text": vmraid._("Assignment closed by {0}").format(get_fullname(vmraid.session.user)),
					"comment_type": "Assignment Completed"
				}

	def on_update(self):
		if self._assignment:
			self.add_assign_comment(**self._assignment)

		self.update_in_reference()

	def on_trash(self):
		# unlink todo from linked comments
		vmraid.db.sql("""
			delete from `tabCommunication Link`
			where link_doctype=%(doctype)s and link_name=%(name)s""", {
				"doctype": self.doctype, "name": self.name
		})

		self.update_in_reference()

	def add_assign_comment(self, text, comment_type):
		if not (self.reference_type and self.reference_name):
			return

		vmraid.get_doc(self.reference_type, self.reference_name).add_comment(comment_type, text)

	def update_in_reference(self):
		if not (self.reference_type and self.reference_name):
			return

		try:
			assignments = [d[0] for d in vmraid.get_all("ToDo",
				filters={
					"reference_type": self.reference_type,
					"reference_name": self.reference_name,
					"status": ("!=", "Cancelled")
				},
				fields=["owner"], as_list=True)]

			assignments.reverse()
			vmraid.db.set_value(self.reference_type, self.reference_name,
				"_assign", json.dumps(assignments), update_modified=False)

		except Exception as e:
			if vmraid.db.is_table_missing(e) and vmraid.flags.in_install:
				# no table
				return

			elif vmraid.db.is_column_missing(e):
				from vmraid.database.schema import add_column
				add_column(self.reference_type, "_assign", "Text")
				self.update_in_reference()

			else:
				raise

# NOTE: todo is viewable if a user is an owner, or set as assigned_to value, or has any role that is allowed to access ToDo doctype.
def on_doctype_update():
	vmraid.db.add_index("ToDo", ["reference_type", "reference_name"])

def get_permission_query_conditions(user):
	if not user: user = vmraid.session.user

	todo_roles = vmraid.permissions.get_doctype_roles('ToDo')
	if 'All' in todo_roles: 
		todo_roles.remove('All')

	if any(check in todo_roles for check in vmraid.get_roles(user)):
		return None
	else:
		return """(`tabToDo`.owner = {user} or `tabToDo`.assigned_by = {user})"""\
			.format(user=vmraid.db.escape(user))

def has_permission(doc, ptype="read", user=None):
	user = user or vmraid.session.user
	todo_roles = vmraid.permissions.get_doctype_roles('ToDo', ptype)
	if 'All' in todo_roles: 
		todo_roles.remove('All')

	if any(check in todo_roles for check in vmraid.get_roles(user)):
		return True
	else:
		return doc.owner==user or doc.assigned_by==user

@vmraid.whitelist()
def new_todo(description):
	vmraid.get_doc({
		'doctype': 'ToDo',
		'description': description
	}).insert()
