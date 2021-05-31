# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import vmraid
import os
import redis

redis_server = None


@vmraid.whitelist()
def get_pending_tasks_for_doc(doctype, docname):
	return vmraid.db.sql_list("select name from `tabAsync Task` where status in ('Queued', 'Running') and reference_doctype=%s and reference_name=%s", (doctype, docname))


def publish_progress(percent, title=None, doctype=None, docname=None, description=None):
	publish_realtime('progress', {'percent': percent, 'title': title, 'description': description},
		user=vmraid.session.user, doctype=doctype, docname=docname)


def publish_realtime(event=None, message=None, room=None,
	user=None, doctype=None, docname=None, task_id=None,
	after_commit=False):
	"""Publish real-time updates

	:param event: Event name, like `task_progress` etc. that will be handled by the client (default is `task_progress` if within task or `global`)
	:param message: JSON message object. For async must contain `task_id`
	:param room: Room in which to publish update (default entire site)
	:param user: Transmit to user
	:param doctype: Transmit to doctype, docname
	:param docname: Transmit to doctype, docname
	:param after_commit: (default False) will emit after current transaction is committed"""
	if message is None:
		message = {}

	if event is None:
		if getattr(vmraid.local, "task_id", None):
			event = "task_progress"
		else:
			event = "global"

	if event=='msgprint' and not user:
		user = vmraid.session.user

	if not room:
		if not task_id and hasattr(vmraid.local, "task_id"):
			task_id = vmraid.local.task_id

		if task_id:
			room = get_task_progress_room(task_id)
			if not "task_id" in message:
				message["task_id"] = task_id

			after_commit = False
		elif user:
			room = get_user_room(user)
		elif doctype and docname:
			room = get_doc_room(doctype, docname)
		else:
			room = get_site_room()
	else:
		# vmraid.chat
		room = get_chat_room(room)
		# end vmraid.chat

	if after_commit:
		params = [event, message, room]
		if not params in vmraid.local.realtime_log:
			vmraid.local.realtime_log.append(params)
	else:
		emit_via_redis(event, message, room)


def emit_via_redis(event, message, room):
	"""Publish real-time updates via redis

	:param event: Event name, like `task_progress` etc.
	:param message: JSON message object. For async must contain `task_id`
	:param room: name of the room"""
	r = get_redis_server()

	try:
		r.publish('events', vmraid.as_json({'event': event, 'message': message, 'room': room}))
	except redis.exceptions.ConnectionError:
		# print(vmraid.get_traceback())
		pass


def get_redis_server():
	"""returns redis_socketio connection."""
	global redis_server
	if not redis_server:
		from redis import Redis
		redis_server = Redis.from_url(vmraid.conf.redis_socketio
			or "redis://localhost:12311")
	return redis_server


@vmraid.whitelist(allow_guest=True)
def can_subscribe_doc(doctype, docname):
	if os.environ.get('CI'):
		return True

	from vmraid.sessions import Session
	from vmraid.exceptions import PermissionError
	session = Session(None, resume=True).get_session_data()
	if not vmraid.has_permission(user=session.user, doctype=doctype, doc=docname, ptype='read'):
		raise PermissionError()

	return True

@vmraid.whitelist(allow_guest=True)
def get_user_info():
	from vmraid.sessions import Session
	session = Session(None, resume=True).get_session_data()
	return {
		'user': session.user,
	}

def get_doc_room(doctype, docname):
	return ''.join([vmraid.local.site, ':doc:', doctype, '/', docname])

def get_user_room(user):
	return ''.join([vmraid.local.site, ':user:', user])

def get_site_room():
	return ''.join([vmraid.local.site, ':all'])

def get_task_progress_room(task_id):
	return "".join([vmraid.local.site, ":task_progress:", task_id])

def get_chat_room(room):
	room = ''.join([vmraid.local.site, ":room:", room])

	return room
