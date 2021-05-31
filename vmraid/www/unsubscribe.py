from __future__ import unicode_literals
import vmraid
from vmraid.utils.verified_command import verify_request
from vmraid.email.doctype.newsletter.newsletter import confirmed_unsubscribe

no_cache = True

def get_context(context):
	vmraid.flags.ignore_permissions = True
	# Called for confirmation.
	if "email" in vmraid.form_dict:
		if verify_request():
			user_email = vmraid.form_dict["email"]
			context.email = user_email
			title = vmraid.form_dict["name"]
			context.email_groups = get_email_groups(user_email)
			context.current_group = get_current_groups(title)
			context.status = "waiting_for_confirmation"

	# Called when form is submitted.
	elif "user_email" in vmraid.form_dict:
		context.status = "unsubscribed"
		email = vmraid.form_dict['user_email']
		email_group = get_email_groups(email)
		for group in email_group:
			if group.email_group in vmraid.form_dict:
				confirmed_unsubscribe(email, group.email_group)

	# Called on Invalid or unsigned request.
	else:
		context.status = "invalid"

def get_email_groups(user_email):
	# Return the all email_groups in which the email has been registered.
	return vmraid.get_all("Email Group Member",
		fields=["email_group"],
		filters={"email": user_email, "unsubscribed": 0})


def get_current_groups(name):
	# Return current group by which the mail has been sent.
	return vmraid.db.get_all("Newsletter Email Group",
		fields=["email_group"],
		filters={"parent":name, "parenttype":"Newsletter"})