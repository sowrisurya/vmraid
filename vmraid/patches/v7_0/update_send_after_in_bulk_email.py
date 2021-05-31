from __future__ import unicode_literals
import vmraid
from vmraid.utils import now_datetime

def execute():
	vmraid.db.sql('update `tabEmail Queue` set send_after=%s where send_after is null', now_datetime())