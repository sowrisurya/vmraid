# -*- coding: utf-8 -*-
# Copyright (c) 2015, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.model.document import Document
from vmraid import _

class OAuthProviderSettings(Document):
	pass

def get_oauth_settings():
	"""Returns oauth settings"""
	out = vmraid._dict({
		"skip_authorization" : vmraid.db.get_value("OAuth Provider Settings", None, "skip_authorization")
	})

	return out