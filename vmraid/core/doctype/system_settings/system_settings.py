# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.model import no_value_fields
from vmraid.translate import set_default_language
from vmraid.utils import cint, today
from vmraid.utils.momentjs import get_all_timezones
from vmraid.twofactor import toggle_two_factor_auth

class SystemSettings(Document):
	def validate(self):
		enable_password_policy = cint(self.enable_password_policy) and True or False
		minimum_password_score = cint(getattr(self, 'minimum_password_score', 0)) or 0
		if enable_password_policy and minimum_password_score <= 0:
			vmraid.throw(_("Please select Minimum Password Score"))
		elif not enable_password_policy:
			self.minimum_password_score = ""

		for key in ("session_expiry", "session_expiry_mobile"):
			if self.get(key):
				parts = self.get(key).split(":")
				if len(parts)!=2 or not (cint(parts[0]) or cint(parts[1])):
					vmraid.throw(_("Session Expiry must be in format {0}").format("hh:mm"))

		if self.enable_two_factor_auth:
			if self.two_factor_method=='SMS':
				if not vmraid.db.get_value('SMS Settings', None, 'sms_gateway_url'):
					vmraid.throw(_('Please setup SMS before setting it as an authentication method, via SMS Settings'))
			toggle_two_factor_auth(True, roles=['All'])
		else:
			self.bypass_2fa_for_retricted_ip_users = 0
			self.bypass_restrict_ip_check_if_2fa_enabled = 0

		vmraid.flags.update_last_reset_password_date = False
		if (self.force_user_to_reset_password and
			not cint(vmraid.db.get_single_value("System Settings", "force_user_to_reset_password"))):
			vmraid.flags.update_last_reset_password_date = True

	def on_update(self):
		for df in self.meta.get("fields"):
			if df.fieldtype not in no_value_fields and self.has_value_changed(df.fieldname):
				vmraid.db.set_default(df.fieldname, self.get(df.fieldname))

		if self.language:
			set_default_language(self.language)

		vmraid.cache().delete_value('system_settings')
		vmraid.cache().delete_value('time_zone')
		vmraid.local.system_settings = {}

		if vmraid.flags.update_last_reset_password_date:
			update_last_reset_password_date()

def update_last_reset_password_date():
	vmraid.db.sql(""" UPDATE `tabUser`
		SET
			last_password_reset_date = %s
		WHERE
			last_password_reset_date is null""", today())

@vmraid.whitelist()
def load():
	if not "System Manager" in vmraid.get_roles():
		vmraid.throw(_("Not permitted"), vmraid.PermissionError)

	all_defaults = vmraid.db.get_defaults()
	defaults = {}

	for df in vmraid.get_meta("System Settings").get("fields"):
		if df.fieldtype in ("Select", "Data"):
			defaults[df.fieldname] = all_defaults.get(df.fieldname)

	return {
		"timezones": get_all_timezones(),
		"defaults": defaults
	}
