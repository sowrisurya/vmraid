# -*- coding: utf-8 -*-
# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.model.document import Document

class UnhandledEmail(Document):
	pass


def remove_old_unhandled_emails():
	vmraid.db.sql("""DELETE FROM `tabUnhandled Email`
	WHERE creation < %s""", vmraid.utils.add_days(vmraid.utils.nowdate(), -30))
