from __future__ import unicode_literals
import vmraid
from   vmraid import _

session = vmraid.session

def authenticate(user, raise_err = True):
	if session.user == 'Guest':
		if not vmraid.db.exists('Chat Token', user):
			if raise_err:
				vmraid.throw(_("Sorry, you're not authorized."))
			else:
				return False
		else:
			return True
	else:
		if user != session.user:
			if raise_err:
				vmraid.throw(_("Sorry, you're not authorized."))
			else:
				return False
		else:
			return True