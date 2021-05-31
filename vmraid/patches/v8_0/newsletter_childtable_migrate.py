# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doc('email', 'doctype', 'newsletter_email_group')
	vmraid.reload_doctype('Newsletter')

	if "email_group" not in vmraid.db.get_table_columns("Newsletter"):
		return
		
	newsletters = vmraid.get_all("Newsletter", fields=["name", "email_group"])
	for newsletter in newsletters:
		if newsletter.email_group:
			newsletter_doc = vmraid.get_doc("Newsletter", newsletter.name)
			if not newsletter_doc.get("email_group"):
				newsletter_doc.append("email_group", {
					"email_group": newsletter.email_group,
				})
				newsletter_doc.flags.ignore_validate = True
				newsletter_doc.flags.ignore_mandatory = True
				newsletter_doc.save()
