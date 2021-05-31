# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
"""
Boot session from cache or build

Session bootstraps info needed by common client side activities including
permission, homepage, default variables, system defaults etc
"""
import vmraid, json
from vmraid import _
import vmraid.utils
from vmraid.utils import cint, cstr, get_assets_json
import vmraid.model.meta
import vmraid.defaults
import vmraid.translate
import redis
from six.moves.urllib.parse import unquote
from six import text_type
from vmraid.cache_manager import clear_user_cache

@vmraid.whitelist(allow_guest=True)
def clear(user=None):
	vmraid.local.session_obj.update(force=True)
	vmraid.local.db.commit()
	clear_user_cache(vmraid.session.user)
	vmraid.response['message'] = _("Cache Cleared")

def clear_sessions(user=None, keep_current=False, device=None, force=False):
	'''Clear other sessions of the current user. Called at login / logout

	:param user: user name (default: current user)
	:param keep_current: keep current session (default: false)
	:param device: delete sessions of this device (default: desktop, mobile)
	:param force: triggered by the user (default false)
	'''

	reason = "Logged In From Another Session"
	if force:
		reason = "Force Logged out by the user"

	for sid in get_sessions_to_clear(user, keep_current, device):
		delete_session(sid, reason=reason)

def get_sessions_to_clear(user=None, keep_current=False, device=None):
	'''Returns sessions of the current user. Called at login / logout

	:param user: user name (default: current user)
	:param keep_current: keep current session (default: false)
	:param device: delete sessions of this device (default: desktop, mobile)
	'''
	if not user:
		user = vmraid.session.user

	if not device:
		device = ("desktop", "mobile")

	if not isinstance(device, (tuple, list)):
		device = (device,)

	offset = 0
	if user == vmraid.session.user:
		simultaneous_sessions = vmraid.db.get_value('User', user, 'simultaneous_sessions') or 1
		offset = simultaneous_sessions - 1

	condition = ''
	if keep_current:
		condition = ' AND sid != {0}'.format(vmraid.db.escape(vmraid.session.sid))

	return vmraid.db.sql_list("""
		SELECT `sid` FROM `tabSessions`
		WHERE `tabSessions`.user=%(user)s
		AND device in %(device)s
		{condition}
		ORDER BY `lastupdate` DESC
		LIMIT 100 OFFSET {offset}""".format(condition=condition, offset=offset),
		{"user": user, "device": device})

def delete_session(sid=None, user=None, reason="Session Expired"):
	from vmraid.core.doctype.activity_log.feed import logout_feed

	vmraid.cache().hdel("session", sid)
	vmraid.cache().hdel("last_db_session_update", sid)
	if sid and not user:
		user_details = vmraid.db.sql("""select user from tabSessions where sid=%s""", sid, as_dict=True)
		if user_details: user = user_details[0].get("user")

	logout_feed(user, reason)
	vmraid.db.sql("""delete from tabSessions where sid=%s""", sid)
	vmraid.db.commit()

def clear_all_sessions(reason=None):
	"""This effectively logs out all users"""
	vmraid.only_for("Administrator")
	if not reason: reason = "Deleted All Active Session"
	for sid in vmraid.db.sql_list("select sid from `tabSessions`"):
		delete_session(sid, reason=reason)

def get_expired_sessions():
	'''Returns list of expired sessions'''
	expired = []
	for device in ("desktop", "mobile"):
		expired += vmraid.db.sql_list("""SELECT `sid`
				FROM `tabSessions`
				WHERE (NOW() - `lastupdate`) > %s
				AND device = %s""", (get_expiry_period_for_query(device), device))

	return expired

def clear_expired_sessions():
	"""This function is meant to be called from scheduler"""
	for sid in get_expired_sessions():
		delete_session(sid, reason="Session Expired")

def get():
	"""get session boot info"""
	from vmraid.boot import get_bootinfo, get_unseen_notes
	from vmraid.utils.change_log import get_change_log

	bootinfo = None
	if not getattr(vmraid.conf,'disable_session_cache', None):
		# check if cache exists
		bootinfo = vmraid.cache().hget("bootinfo", vmraid.session.user)
		if bootinfo:
			bootinfo['from_cache'] = 1
			bootinfo["user"]["recent"] = json.dumps(\
				vmraid.cache().hget("user_recent", vmraid.session.user))

	if not bootinfo:
		# if not create it
		bootinfo = get_bootinfo()
		vmraid.cache().hset("bootinfo", vmraid.session.user, bootinfo)
		try:
			vmraid.cache().ping()
		except redis.exceptions.ConnectionError:
			message = _("Redis cache server not running. Please contact Administrator / Tech support")
			if 'messages' in bootinfo:
				bootinfo['messages'].append(message)
			else:
				bootinfo['messages'] = [message]

		# check only when clear cache is done, and don't cache this
		if vmraid.local.request:
			bootinfo["change_log"] = get_change_log()

	bootinfo["metadata_version"] = vmraid.cache().get_value("metadata_version")
	if not bootinfo["metadata_version"]:
		bootinfo["metadata_version"] = vmraid.reset_metadata_version()

	bootinfo.notes = get_unseen_notes()
	bootinfo.assets_json = get_assets_json()

	for hook in vmraid.get_hooks("extend_bootinfo"):
		vmraid.get_attr(hook)(bootinfo=bootinfo)

	bootinfo["lang"] = vmraid.translate.get_user_lang()
	bootinfo["disable_async"] = vmraid.conf.disable_async

	bootinfo["setup_complete"] = cint(vmraid.db.get_single_value('System Settings', 'setup_complete'))
	bootinfo["is_first_startup"] = cint(vmraid.db.get_single_value('System Settings', 'is_first_startup'))

	return bootinfo

def get_csrf_token():
	if not vmraid.local.session.data.csrf_token:
		generate_csrf_token()

	return vmraid.local.session.data.csrf_token

def generate_csrf_token():
	vmraid.local.session.data.csrf_token = vmraid.generate_hash()
	vmraid.local.session_obj.update(force=True)

class Session:
	def __init__(self, user, resume=False, full_name=None, user_type=None):
		self.sid = cstr(vmraid.form_dict.get('sid') or
			unquote(vmraid.request.cookies.get('sid', 'Guest')))
		self.user = user
		self.device = vmraid.form_dict.get("device") or "desktop"
		self.user_type = user_type
		self.full_name = full_name
		self.data = vmraid._dict({'data': vmraid._dict({})})
		self.time_diff = None

		# set local session
		vmraid.local.session = self.data

		if resume:
			self.resume()

		else:
			if self.user:
				self.start()

	def start(self):
		"""start a new session"""
		# generate sid
		if self.user=='Guest':
			sid = 'Guest'
		else:
			sid = vmraid.generate_hash()

		self.data.user = self.user
		self.data.sid = sid
		self.data.data.user = self.user
		self.data.data.session_ip = vmraid.local.request_ip
		if self.user != "Guest":
			self.data.data.update({
				"last_updated": vmraid.utils.now(),
				"session_expiry": get_expiry_period(self.device),
				"full_name": self.full_name,
				"user_type": self.user_type,
				"device": self.device,
				"session_country": get_geo_ip_country(vmraid.local.request_ip) if vmraid.local.request_ip else None,
			})

		# insert session
		if self.user!="Guest":
			self.insert_session_record()

			# update user
			user = vmraid.get_doc("User", self.data['user'])
			vmraid.db.sql("""UPDATE `tabUser`
				SET
					last_login = %(now)s,
					last_ip = %(ip)s,
					last_active = %(now)s
				WHERE name=%(name)s""", {
					'now': vmraid.utils.now(),
					'ip': vmraid.local.request_ip,
					'name': self.data['user']
				})
			user.run_notifications("before_change")
			user.run_notifications("on_update")
			vmraid.db.commit()

	def insert_session_record(self):
		vmraid.db.sql("""insert into `tabSessions`
			(`sessiondata`, `user`, `lastupdate`, `sid`, `status`, `device`)
			values (%s , %s, NOW(), %s, 'Active', %s)""",
				(str(self.data['data']), self.data['user'], self.data['sid'], self.device))

		# also add to memcache
		vmraid.cache().hset("session", self.data.sid, self.data)

	def resume(self):
		"""non-login request: load a session"""
		import vmraid
		from vmraid.auth import validate_ip_address
		data = self.get_session_record()

		if data:
			# set language
			self.data.update({'data': data, 'user':data.user, 'sid': self.sid})
			self.user = data.user
			validate_ip_address(self.user)
			self.device = data.device
		else:
			self.start_as_guest()

		if self.sid != "Guest":
			vmraid.local.user_lang = vmraid.translate.get_user_lang(self.data.user)
			vmraid.local.lang = vmraid.local.user_lang

	def get_session_record(self):
		"""get session record, or return the standard Guest Record"""
		from vmraid.auth import clear_cookies
		r = self.get_session_data()

		if not r:
			vmraid.response["session_expired"] = 1
			clear_cookies()
			self.sid = "Guest"
			r = self.get_session_data()

		return r

	def get_session_data(self):
		if self.sid=="Guest":
			return vmraid._dict({"user":"Guest"})

		data = self.get_session_data_from_cache()
		if not data:
			data = self.get_session_data_from_db()
		return data

	def get_session_data_from_cache(self):
		data = vmraid.cache().hget("session", self.sid)
		if data:
			data = vmraid._dict(data)
			session_data = data.get("data", {})

			# set user for correct timezone
			self.time_diff = vmraid.utils.time_diff_in_seconds(vmraid.utils.now(),
				session_data.get("last_updated"))
			expiry = get_expiry_in_seconds(session_data.get("session_expiry"))

			if self.time_diff > expiry:
				self._delete_session()
				data = None

		return data and data.data

	def get_session_data_from_db(self):
		self.device = vmraid.db.sql('SELECT `device` FROM `tabSessions` WHERE `sid`=%s', self.sid)
		self.device = self.device and self.device[0][0] or 'desktop'

		rec = vmraid.db.sql("""
			SELECT `user`, `sessiondata`
			FROM `tabSessions` WHERE `sid`=%s AND
			(NOW() - lastupdate) < %s
			""", (self.sid, get_expiry_period_for_query(self.device)))

		if rec:
			data = vmraid._dict(vmraid.safe_eval(rec and rec[0][1] or '{}'))
			data.user = rec[0][0]
		else:
			self._delete_session()
			data = None

		return data

	def _delete_session(self):
		delete_session(self.sid, reason="Session Expired")

	def start_as_guest(self):
		"""all guests share the same 'Guest' session"""
		self.user = "Guest"
		self.start()

	def update(self, force=False):
		"""extend session expiry"""
		if (vmraid.session['user'] == "Guest" or vmraid.form_dict.cmd=="logout"):
			return

		now = vmraid.utils.now()

		self.data['data']['last_updated'] = now
		self.data['data']['lang'] = text_type(vmraid.lang)

		# update session in db
		last_updated = vmraid.cache().hget("last_db_session_update", self.sid)
		time_diff = vmraid.utils.time_diff_in_seconds(now, last_updated) if last_updated else None

		# database persistence is secondary, don't update it too often
		updated_in_db = False
		if force or (time_diff==None) or (time_diff > 600):
			# update sessions table
			vmraid.db.sql("""update `tabSessions` set sessiondata=%s,
				lastupdate=NOW() where sid=%s""" , (str(self.data['data']),
				self.data['sid']))

			# update last active in user table
			vmraid.db.sql("""update `tabUser` set last_active=%(now)s where name=%(name)s""", {
				"now": now,
				"name": vmraid.session.user
			})

			vmraid.db.commit()
			vmraid.cache().hset("last_db_session_update", self.sid, now)

			updated_in_db = True

		# set in memcache
		vmraid.cache().hset("session", self.sid, self.data)

		return updated_in_db

def get_expiry_period_for_query(device=None):
	if vmraid.db.db_type == 'postgres':
		return get_expiry_period(device)
	else:
		return get_expiry_in_seconds(device=device)

def get_expiry_in_seconds(expiry=None, device=None):
	if not expiry:
		expiry = get_expiry_period(device)
	parts = expiry.split(":")
	return (cint(parts[0]) * 3600) + (cint(parts[1]) * 60) + cint(parts[2])

def get_expiry_period(device="desktop"):
	if device=="mobile":
		key = "session_expiry_mobile"
		default = "720:00:00"
	else:
		key = "session_expiry"
		default = "06:00:00"

	exp_sec = vmraid.defaults.get_global_default(key) or default

	# incase seconds is missing
	if len(exp_sec.split(':')) == 2:
		exp_sec = exp_sec + ':00'

	return exp_sec

def get_geo_from_ip(ip_addr):
	try:
		from geolite2 import geolite2
		with geolite2 as f:
			reader = f.reader()
			data   = reader.get(ip_addr)

			return vmraid._dict(data)
	except ImportError:
		return
	except ValueError:
		return
	except TypeError:
		return

def get_geo_ip_country(ip_addr):
	match = get_geo_from_ip(ip_addr)
	if match:
		return match.country
