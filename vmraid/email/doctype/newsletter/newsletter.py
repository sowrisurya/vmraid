# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import vmraid
import vmraid.utils
from vmraid import throw, _
from vmraid.website.website_generator import WebsiteGenerator
from vmraid.utils.verified_command import get_signed_params, verify_request
from vmraid.email.queue import send
from vmraid.email.doctype.email_group.email_group import add_subscribers
from vmraid.utils import parse_addr, now_datetime, markdown, validate_email_address

class Newsletter(WebsiteGenerator):
	def onload(self):
		if self.email_sent:
			self.get("__onload").status_count = dict(vmraid.db.sql("""select status, count(name)
				from `tabEmail Queue` where reference_doctype=%s and reference_name=%s
				group by status""", (self.doctype, self.name))) or None

	def validate(self):
		self.route = "newsletters/" + self.name
		if self.send_from:
			validate_email_address(self.send_from, True)

	@vmraid.whitelist()
	def test_send(self, doctype="Lead"):
		self.recipients = vmraid.utils.split_emails(self.test_email_id)
		self.queue_all(test_email=True)
		vmraid.msgprint(_("Test email sent to {0}").format(self.test_email_id))

	@vmraid.whitelist()
	def send_emails(self):
		"""send emails to leads and customers"""
		if self.email_sent:
			throw(_("Newsletter has already been sent"))

		self.recipients = self.get_recipients()

		if self.recipients:
			self.queue_all()
			vmraid.msgprint(_("Email queued to {0} recipients").format(len(self.recipients)))

		else:
			vmraid.msgprint(_("Newsletter should have atleast one recipient"))

	def queue_all(self, test_email=False):
		if not self.get("recipients"):
			# in case it is called via worker
			self.recipients = self.get_recipients()

		self.validate_send()

		sender = self.send_from or vmraid.utils.get_formatted_email(self.owner)

		if not vmraid.flags.in_test:
			vmraid.db.auto_commit_on_many_writes = True

		attachments = []
		if self.send_attachments:
			files = vmraid.get_all("File", fields=["name"], filters={"attached_to_doctype": "Newsletter",
				"attached_to_name": self.name}, order_by="creation desc")

			for file in files:
				try:
					# these attachments will be attached on-demand
					# and won't be stored in the message
					attachments.append({"fid": file.name})
				except IOError:
					vmraid.throw(_("Unable to find attachment {0}").format(file.name))

		args = {
			"message": self.get_message(),
			"name": self.name
		}
		vmraid.sendmail(recipients=self.recipients, sender=sender,
			subject=self.subject, message=self.get_message(), template="newsletter",
			reference_doctype=self.doctype, reference_name=self.name,
			add_unsubscribe_link=self.send_unsubscribe_link, attachments=attachments,
			unsubscribe_method="/unsubscribe",
			unsubscribe_params={"name": self.name},
			send_priority=0, queue_separately=True, args=args)

		if not vmraid.flags.in_test:
			vmraid.db.auto_commit_on_many_writes = False

		if not test_email:
			self.db_set("email_sent", 1)
			self.db_set("schedule_send", now_datetime())
			self.db_set("scheduled_to_send", len(self.recipients))

	def get_message(self):
		if self.content_type == "HTML":
			return vmraid.render_template(self.message_html, {"doc": self.as_dict()})
		return {
			'Rich Text': self.message,
			'Markdown': markdown(self.message_md)
		}[self.content_type or 'Rich Text']

	def get_recipients(self):
		"""Get recipients from Email Group"""
		recipients_list = []
		for email_group in get_email_groups(self.name):
			for d in vmraid.db.get_all("Email Group Member", ["email"],
				{"unsubscribed": 0, "email_group": email_group.email_group}):
					recipients_list.append(d.email)
		return list(set(recipients_list))

	def validate_send(self):
		if self.get("__islocal"):
			throw(_("Please save the Newsletter before sending"))

		if not self.recipients:
			vmraid.throw(_("Newsletter should have at least one recipient"))

	def get_context(self, context):
		newsletters = get_newsletter_list("Newsletter", None, None, 0)
		if newsletters:
			newsletter_list = [d.name for d in newsletters]
			if self.name not in newsletter_list:
				vmraid.redirect_to_message(_('Permission Error'),
					_("You are not permitted to view the newsletter."))
				vmraid.local.flags.redirect_location = vmraid.local.response.location
				raise vmraid.Redirect
			else:
				context.attachments = get_attachments(self.name)
		context.no_cache = 1
		context.show_sidebar = True


def get_attachments(name):
	return vmraid.get_all("File",
			fields=["name", "file_name", "file_url", "is_private"],
			filters = {"attached_to_name": name, "attached_to_doctype": "Newsletter", "is_private":0})


def get_email_groups(name):
	return vmraid.db.get_all("Newsletter Email Group", ["email_group"],{"parent":name, "parenttype":"Newsletter"})


@vmraid.whitelist(allow_guest=True)
def confirmed_unsubscribe(email, group):
	""" unsubscribe the email(user) from the mailing list(email_group) """
	vmraid.flags.ignore_permissions=True
	doc = vmraid.get_doc("Email Group Member", {"email": email, "email_group": group})
	if not doc.unsubscribed:
		doc.unsubscribed = 1
		doc.save(ignore_permissions = True)

def create_lead(email_id):
	"""create a lead if it does not exist"""
	from vmraid.model.naming import get_default_naming_series
	full_name, email_id = parse_addr(email_id)
	if vmraid.db.get_value("Lead", {"email_id": email_id}):
		return

	lead = vmraid.get_doc({
		"doctype": "Lead",
		"email_id": email_id,
		"lead_name": full_name or email_id,
		"status": "Lead",
		"naming_series": get_default_naming_series("Lead"),
		"company": vmraid.db.get_default("Company"),
		"source": "Email"
	})
	lead.insert()


@vmraid.whitelist(allow_guest=True)
def subscribe(email, email_group=_('Website')):
	url = vmraid.utils.get_url("/api/method/vmraid.email.doctype.newsletter.newsletter.confirm_subscription") +\
		"?" + get_signed_params({"email": email, "email_group": email_group})

	email_template = vmraid.db.get_value('Email Group', email_group, ['confirmation_email_template'])

	content=''
	if email_template:
		args = dict(
			email=email,
			confirmation_url=url,
			email_group=email_group
		)

		email_template = vmraid.get_doc("Email Template", email_template)
		content = vmraid.render_template(email_template.response, args)

	if not content:
		messages = (
			_("Thank you for your interest in subscribing to our updates"),
			_("Please verify your Email Address"),
			url,
			_("Click here to verify")
		)

		content = """
		<p>{0}. {1}.</p>
		<p><a href="{2}">{3}</a></p>
		""".format(*messages)

	vmraid.sendmail(email, subject=getattr('email_template', 'subject', '') or _("Confirm Your Email"), content=content, now=True)

@vmraid.whitelist(allow_guest=True)
def confirm_subscription(email, email_group=_('Website')):
	if not verify_request():
		return

	if not vmraid.db.exists("Email Group", email_group):
		vmraid.get_doc({
			"doctype": "Email Group",
			"title": email_group
		}).insert(ignore_permissions=True)

	vmraid.flags.ignore_permissions = True

	add_subscribers(email_group, email)
	vmraid.db.commit()

	vmraid.respond_as_web_page(_("Confirmed"),
		_("{0} has been successfully added to the Email Group.").format(email),
		indicator_color='green')


def send_newsletter(newsletter):
	try:
		doc = vmraid.get_doc("Newsletter", newsletter)
		doc.queue_all()

	except:
		vmraid.db.rollback()

		# wasn't able to send emails :(
		doc.db_set("email_sent", 0)
		vmraid.db.commit()

		vmraid.log_error(title='Send Newsletter')

		raise

	else:
		vmraid.db.commit()


def get_list_context(context=None):
	context.update({
		"show_sidebar": True,
		"show_search": True,
		'no_breadcrumbs': True,
		"title": _("Newsletter"),
		"get_list": get_newsletter_list,
		"row_template": "email/doctype/newsletter/templates/newsletter_row.html",
	})


def get_newsletter_list(doctype, txt, filters, limit_start, limit_page_length=20, order_by="modified"):
	email_group_list = vmraid.db.sql('''SELECT eg.name
		FROM `tabEmail Group` eg, `tabEmail Group Member` egm
		WHERE egm.unsubscribed=0
		AND eg.name=egm.email_group
		AND egm.email = %s''', vmraid.session.user)
	email_group_list = [d[0] for d in email_group_list]

	if email_group_list:
		return vmraid.db.sql('''SELECT n.name, n.subject, n.message, n.modified
			FROM `tabNewsletter` n, `tabNewsletter Email Group` neg
			WHERE n.name = neg.parent
			AND n.email_sent=1
			AND n.published=1
			AND neg.email_group in ({0})
			ORDER BY n.modified DESC LIMIT {1} OFFSET {2}
			'''.format(','.join(['%s'] * len(email_group_list)),
					limit_page_length, limit_start), email_group_list, as_dict=1)

def send_scheduled_email():
	"""Send scheduled newsletter to the recipients."""
	scheduled_newsletter = vmraid.get_all('Newsletter', filters = {
		'schedule_send': ('<=', now_datetime()),
		'email_sent': 0,
		'schedule_sending': 1
	}, fields = ['name'], ignore_ifnull=True)
	for newsletter in scheduled_newsletter:
		send_newsletter(newsletter.name)
