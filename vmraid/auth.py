# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import datetime

from vmraid import _
import vmraid
import vmraid.database
import vmraid.utils
from vmraid.utils import cint, flt, get_datetime, datetime, date_diff, today
import vmraid.utils.user
from vmraid import conf
from vmraid.sessions import Session, clear_sessions, delete_session
from vmraid.modules.patch_handler import check_session_stopped
from vmraid.translate import get_lang_code
from vmraid.utils.password import check_password, delete_login_failed_cache
from vmraid.core.doctype.activity_log.activity_log import add_authentication_log
from vmraid.twofactor import (should_run_2fa, authenticate_for_2factor,
	confirm_otp_token, get_cached_user_pass)
from vmraid.website.utils import get_home_page

from six.moves.urllib.parse import quote


class HTTPRequest:
	def __init__(self):
		# Get Environment variables
		self.domain = vmraid.request.host
		if self.domain and self.domain.startswith('www.'):
			self.domain = self.domain[4:]

		if vmraid.get_request_header('X-Forwarded-For'):
			vmraid.local.request_ip = (vmraid.get_request_header('X-Forwarded-For').split(",")[0]).strip()

		elif vmraid.get_request_header('REMOTE_ADDR'):
			vmraid.local.request_ip = vmraid.get_request_header('REMOTE_ADDR')

		else:
			vmraid.local.request_ip = '127.0.0.1'

		# language
		self.set_lang()

		# load cookies
		vmraid.local.cookie_manager = CookieManager()

		# set db
		self.connect()

		# login
		vmraid.local.login_manager = LoginManager()

		if vmraid.form_dict._lang:
			lang = get_lang_code(vmraid.form_dict._lang)
			if lang:
				vmraid.local.lang = lang

		self.validate_csrf_token()

		# write out latest cookies
		vmraid.local.cookie_manager.init_cookies()

		# check status
		check_session_stopped()

	def validate_csrf_token(self):
		if vmraid.local.request and vmraid.local.request.method in ("POST", "PUT", "DELETE"):
			if not vmraid.local.session: return
			if not vmraid.local.session.data.csrf_token \
				or vmraid.local.session.data.device=="mobile" \
				or vmraid.conf.get('ignore_csrf', None):
				# not via boot
				return

			csrf_token = vmraid.get_request_header("X-VMRaid-CSRF-Token")
			if not csrf_token and "csrf_token" in vmraid.local.form_dict:
				csrf_token = vmraid.local.form_dict.csrf_token
				del vmraid.local.form_dict["csrf_token"]

			if vmraid.local.session.data.csrf_token != csrf_token:
				vmraid.local.flags.disable_traceback = True
				vmraid.throw(_("Invalid Request"), vmraid.CSRFTokenError)

	def set_lang(self):
		from vmraid.translate import guess_language
		vmraid.local.lang = guess_language()

	def get_db_name(self):
		"""get database name from conf"""
		return conf.db_name

	def connect(self, ac_name = None):
		"""connect to db, from ac_name or db_name"""
		vmraid.local.db = vmraid.database.get_db(user = self.get_db_name(), \
			password = getattr(conf, 'db_password', ''))

class LoginManager:
	def __init__(self):
		self.user = None
		self.info = None
		self.full_name = None
		self.user_type = None

		if vmraid.local.form_dict.get('cmd')=='login' or vmraid.local.request.path=="/api/method/login":
			if self.login()==False: return
			self.resume = False

			# run login triggers
			self.run_trigger('on_session_creation')
		else:
			try:
				self.resume = True
				self.make_session(resume=True)
				self.get_user_info()
				self.set_user_info(resume=True)
			except AttributeError:
				self.user = "Guest"
				self.get_user_info()
				self.make_session()
				self.set_user_info()

	@vmraid.whitelist()
	def login(self):
		# clear cache
		vmraid.clear_cache(user = vmraid.form_dict.get('usr'))
		user, pwd = get_cached_user_pass()
		self.authenticate(user=user, pwd=pwd)
		if self.force_user_to_reset_password():
			doc = vmraid.get_doc("User", self.user)
			vmraid.local.response["redirect_to"] = doc.reset_password(send_email=False, password_expired=True)
			vmraid.local.response["message"] = "Password Reset"
			return False

		if should_run_2fa(self.user):
			authenticate_for_2factor(self.user)
			if not confirm_otp_token(self):
				return False
		self.post_login()

	def post_login(self):
		self.run_trigger('on_login')
		validate_ip_address(self.user)
		self.validate_hour()
		self.get_user_info()
		self.make_session()
		self.setup_boot_cache()
		self.set_user_info()

	def get_user_info(self, resume=False):
		self.info = vmraid.db.get_value("User", self.user,
			["user_type", "first_name", "last_name", "user_image"], as_dict=1)

		self.user_type = self.info.user_type

	def setup_boot_cache(self):
		vmraid.cache_manager.build_table_count_cache()
		vmraid.cache_manager.build_domain_restriced_doctype_cache()
		vmraid.cache_manager.build_domain_restriced_page_cache()

	def set_user_info(self, resume=False):
		# set sid again
		vmraid.local.cookie_manager.init_cookies()

		self.full_name = " ".join(filter(None, [self.info.first_name,
			self.info.last_name]))

		if self.info.user_type=="Website User":
			vmraid.local.cookie_manager.set_cookie("system_user", "no")
			if not resume:
				vmraid.local.response["message"] = "No App"
				vmraid.local.response["home_page"] = '/' + get_home_page()
		else:
			vmraid.local.cookie_manager.set_cookie("system_user", "yes")
			if not resume:
				vmraid.local.response['message'] = 'Logged In'
				vmraid.local.response["home_page"] = "/app"

		if not resume:
			vmraid.response["full_name"] = self.full_name

		# redirect information
		redirect_to = vmraid.cache().hget('redirect_after_login', self.user)
		if redirect_to:
			vmraid.local.response["redirect_to"] = redirect_to
			vmraid.cache().hdel('redirect_after_login', self.user)


		vmraid.local.cookie_manager.set_cookie("full_name", self.full_name)
		vmraid.local.cookie_manager.set_cookie("user_id", self.user)
		vmraid.local.cookie_manager.set_cookie("user_image", self.info.user_image or "")

	def make_session(self, resume=False):
		# start session
		vmraid.local.session_obj = Session(user=self.user, resume=resume,
			full_name=self.full_name, user_type=self.user_type)

		# reset user if changed to Guest
		self.user = vmraid.local.session_obj.user
		vmraid.local.session = vmraid.local.session_obj.data
		self.clear_active_sessions()

	def clear_active_sessions(self):
		"""Clear other sessions of the current user if `deny_multiple_sessions` is not set"""
		if not (cint(vmraid.conf.get("deny_multiple_sessions")) or cint(vmraid.db.get_system_setting('deny_multiple_sessions'))):
			return

		if vmraid.session.user != "Guest":
			clear_sessions(vmraid.session.user, keep_current=True)

	def authenticate(self, user: str = None, pwd: str = None):
		from vmraid.core.doctype.user.user import User

		if not (user and pwd):
			user, pwd = vmraid.form_dict.get('usr'), vmraid.form_dict.get('pwd')
		if not (user and pwd):
			self.fail(_('Incomplete login details'), user=user)

		user = User.find_by_credentials(user, pwd)

		if not user:
			self.fail('Invalid login credentials')

		# Current login flow uses cached credentials for authentication while checking OTP.
		# Incase of OTP check, tracker for auth needs to be disabled(If not, it can remove tracker history as it is going to succeed anyway)
		# Tracker is activated for 2FA incase of OTP.
		ignore_tracker = should_run_2fa(user.name) and ('otp' in vmraid.form_dict)
		tracker = None if ignore_tracker else get_login_attempt_tracker(user.name)

		if not user.is_authenticated:
			tracker and tracker.add_failure_attempt()
			self.fail('Invalid login credentials', user=user.name)
		elif not (user.name == 'Administrator' or user.enabled):
			tracker and tracker.add_failure_attempt()
			self.fail('User disabled or missing', user=user.name)
		else:
			tracker and tracker.add_success_attempt()
		self.user = user.name

	def force_user_to_reset_password(self):
		if not self.user:
			return

		from vmraid.core.doctype.user.user import STANDARD_USERS
		if self.user in STANDARD_USERS:
			return False

		reset_pwd_after_days = cint(vmraid.db.get_single_value("System Settings",
			"force_user_to_reset_password"))

		if reset_pwd_after_days:
			last_password_reset_date = vmraid.db.get_value("User",
				self.user, "last_password_reset_date")  or today()

			last_pwd_reset_days = date_diff(today(), last_password_reset_date)

			if last_pwd_reset_days > reset_pwd_after_days:
				return True

	def check_password(self, user, pwd):
		"""check password"""
		try:
			# returns user in correct case
			return check_password(user, pwd)
		except vmraid.AuthenticationError:
			self.fail('Incorrect password', user=user)

	def fail(self, message, user=None):
		if not user:
			user = _('Unknown User')
		vmraid.local.response['message'] = message
		add_authentication_log(message, user, status="Failed")
		vmraid.db.commit()
		raise vmraid.AuthenticationError

	def run_trigger(self, event='on_login'):
		for method in vmraid.get_hooks().get(event, []):
			vmraid.call(vmraid.get_attr(method), login_manager=self)

	def validate_hour(self):
		"""check if user is logging in during restricted hours"""
		login_before = int(vmraid.db.get_value('User', self.user, 'login_before', ignore=True) or 0)
		login_after = int(vmraid.db.get_value('User', self.user, 'login_after', ignore=True) or 0)

		if not (login_before or login_after):
			return

		from vmraid.utils import now_datetime
		current_hour = int(now_datetime().strftime('%H'))

		if login_before and current_hour > login_before:
			vmraid.throw(_("Login not allowed at this time"), vmraid.AuthenticationError)

		if login_after and current_hour < login_after:
			vmraid.throw(_("Login not allowed at this time"), vmraid.AuthenticationError)

	def login_as_guest(self):
		"""login as guest"""
		self.login_as("Guest")

	def login_as(self, user):
		self.user = user
		self.post_login()

	def logout(self, arg='', user=None):
		if not user: user = vmraid.session.user
		self.run_trigger('on_logout')

		if user == vmraid.session.user:
			delete_session(vmraid.session.sid, user=user, reason="User Manually Logged Out")
			self.clear_cookies()
		else:
			clear_sessions(user)

	def clear_cookies(self):
		clear_cookies()

class CookieManager:
	def __init__(self):
		self.cookies = {}
		self.to_delete = []

	def init_cookies(self):
		if not vmraid.local.session.get('sid'): return

		# sid expires in 3 days
		expires = datetime.datetime.now() + datetime.timedelta(days=3)
		if vmraid.session.sid:
			self.set_cookie("sid", vmraid.session.sid, expires=expires, httponly=True)
		if vmraid.session.session_country:
			self.set_cookie("country", vmraid.session.session_country)

	def set_cookie(self, key, value, expires=None, secure=False, httponly=False, samesite="Lax"):
		if not secure and hasattr(vmraid.local, 'request'):
			secure = vmraid.local.request.scheme == "https"

		# Cordova does not work with Lax
		if vmraid.local.session.data.device == "mobile":
			samesite = None

		self.cookies[key] = {
			"value": value,
			"expires": expires,
			"secure": secure,
			"httponly": httponly,
			"samesite": samesite
		}

	def delete_cookie(self, to_delete):
		if not isinstance(to_delete, (list, tuple)):
			to_delete = [to_delete]

		self.to_delete.extend(to_delete)

	def flush_cookies(self, response):
		for key, opts in self.cookies.items():
			response.set_cookie(key, quote((opts.get("value") or "").encode('utf-8')),
				expires=opts.get("expires"),
				secure=opts.get("secure"),
				httponly=opts.get("httponly"),
				samesite=opts.get("samesite"))

		# expires yesterday!
		expires = datetime.datetime.now() + datetime.timedelta(days=-1)
		for key in set(self.to_delete):
			response.set_cookie(key, "", expires=expires)


@vmraid.whitelist()
def get_logged_user():
	return vmraid.session.user

def clear_cookies():
	if hasattr(vmraid.local, "session"):
		vmraid.session.sid = ""
	vmraid.local.cookie_manager.delete_cookie(["full_name", "user_id", "sid", "user_image", "system_user"])

def validate_ip_address(user):
	"""check if IP Address is valid"""
	user = vmraid.get_cached_doc("User", user) if not vmraid.flags.in_test else vmraid.get_doc("User", user)
	ip_list = user.get_restricted_ip_list()
	if not ip_list:
		return

	system_settings = vmraid.get_cached_doc("System Settings") if not vmraid.flags.in_test else vmraid.get_single("System Settings")
	# check if bypass restrict ip is enabled for all users
	bypass_restrict_ip_check = system_settings.bypass_restrict_ip_check_if_2fa_enabled

	# check if two factor auth is enabled
	if system_settings.enable_two_factor_auth and not bypass_restrict_ip_check:
		# check if bypass restrict ip is enabled for login user
		bypass_restrict_ip_check = user.bypass_restrict_ip_check_if_2fa_enabled

	for ip in ip_list:
		if vmraid.local.request_ip.startswith(ip) or bypass_restrict_ip_check:
			return

	vmraid.throw(_("Access not allowed from this IP Address"), vmraid.AuthenticationError)

def get_login_attempt_tracker(user_name: str, raise_locked_exception: bool = True):
	"""Get login attempt tracker instance.

	:param user_name: Name of the loggedin user
	:param raise_locked_exception: If set, raises an exception incase of user not allowed to login
	"""
	sys_settings = vmraid.get_doc("System Settings")
	track_login_attempts = (sys_settings.allow_consecutive_login_attempts >0)
	tracker_kwargs = {}

	if track_login_attempts:
		tracker_kwargs['lock_interval'] = sys_settings.allow_login_after_fail
		tracker_kwargs['max_consecutive_login_attempts'] = sys_settings.allow_consecutive_login_attempts

	tracker = LoginAttemptTracker(user_name, **tracker_kwargs)

	if raise_locked_exception and track_login_attempts and not tracker.is_user_allowed():
		vmraid.throw(_("Your account has been locked and will resume after {0} seconds")
			.format(sys_settings.allow_login_after_fail), vmraid.SecurityException)
	return tracker


class LoginAttemptTracker(object):
	"""Track login attemts of a user.

	Lock the account for s number of seconds if there have been n consecutive unsuccessful attempts to log in.
	"""
	def __init__(self, user_name: str, max_consecutive_login_attempts: int=3, lock_interval:int = 5*60):
		""" Initialize the tracker.

		:param user_name: Name of the loggedin user
		:param max_consecutive_login_attempts: Maximum allowed consecutive failed login attempts
		:param lock_interval: Locking interval incase of maximum failed attempts
		"""
		self.user_name = user_name
		self.lock_interval = datetime.timedelta(seconds=lock_interval)
		self.max_failed_logins = max_consecutive_login_attempts

	@property
	def login_failed_count(self):
		return vmraid.cache().hget('login_failed_count', self.user_name)

	@login_failed_count.setter
	def login_failed_count(self, count):
		vmraid.cache().hset('login_failed_count', self.user_name, count)

	@login_failed_count.deleter
	def login_failed_count(self):
		vmraid.cache().hdel('login_failed_count', self.user_name)

	@property
	def login_failed_time(self):
		"""First failed login attempt time within lock interval.

		For every user we track only First failed login attempt time within lock interval of time.
		"""
		return vmraid.cache().hget('login_failed_time', self.user_name)

	@login_failed_time.setter
	def login_failed_time(self, timestamp):
		vmraid.cache().hset('login_failed_time', self.user_name, timestamp)

	@login_failed_time.deleter
	def login_failed_time(self):
		vmraid.cache().hdel('login_failed_time', self.user_name)

	def add_failure_attempt(self):
		""" Log user failure attempts into the system.

		Increase the failure count if new failure is with in current lock interval time period, if not reset the login failure count.
		"""
		login_failed_time = self.login_failed_time
		login_failed_count = self.login_failed_count # Consecutive login failure count
		current_time = get_datetime()

		if not (login_failed_time and login_failed_count):
			login_failed_time, login_failed_count = current_time, 0

		if login_failed_time + self.lock_interval > current_time:
			login_failed_count += 1
		else:
			login_failed_time, login_failed_count = current_time, 1

		self.login_failed_time = login_failed_time
		self.login_failed_count = login_failed_count

	def add_success_attempt(self):
		"""Reset login failures.
		"""
		del self.login_failed_count
		del self.login_failed_time

	def is_user_allowed(self) -> bool:
		"""Is user allowed to login

		User is not allowed to login if login failures are greater than threshold within in lock interval from first login failure.
		"""
		login_failed_time = self.login_failed_time
		login_failed_count = self.login_failed_count or 0
		current_time = get_datetime()

		if login_failed_time and login_failed_time + self.lock_interval > current_time and login_failed_count > self.max_failed_logins:
			return False
		return True
