from __future__ import unicode_literals

import vmraid

def execute():
	vmraid.reload_doctype("Notification")
	for e in vmraid.get_all("Notification"):
		notification = vmraid.get_doc("Notification", e.name)
		if notification.event == "Date Change":
			if notification.days_in_advance < 0:
				notification.event = "Days After"
				notification.days_in_advance = -email_alert.days_in_advance
			else:
				notification.event = "Days Before"

			notification.save()
