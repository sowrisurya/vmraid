from __future__ import unicode_literals
from . import __version__ as app_version


app_name = "vmraid"
app_title = "VMRaid Framework"
app_publisher = "VMRaid Technologies"
app_description = "Full stack web framework with Python, Javascript, MariaDB, Redis, Node"
app_icon = "octicon octicon-circuit-board"
app_color = "orange"
source_link = "https://github.com/vmraid/vmraid"
app_license = "MIT"
app_logo_url = '/assets/vmraid/images/vmraid-framework-logo.svg'

develop_version = '13.x.x-develop'

app_email = "info@vmraid.io"

docs_app = "vmraid_io"

translator_url = "https://translate.erpadda.com"

before_install = "vmraid.utils.install.before_install"
after_install = "vmraid.utils.install.after_install"

page_js = {
	"setup-wizard": "public/js/vmraid/setup_wizard.js"
}

# website
app_include_js = [
	"libs.bundle.js",
	"desk.bundle.js",
	"list.bundle.js",
	"form.bundle.js",
	"controls.bundle.js",
	"report.bundle.js",
]
app_include_css = [
	"desk.bundle.css",
	"report.bundle.css",
]

doctype_js = {
	"Web Page": "public/js/vmraid/utils/web_template.js",
	"Website Settings": "public/js/vmraid/utils/web_template.js"
}

web_include_js = [
	"website_script.js"
]

web_include_css = []

email_css = ['email.bundle.css']

website_route_rules = [
	{"from_route": "/blog/<category>", "to_route": "Blog Post"},
	{"from_route": "/kb/<category>", "to_route": "Help Article"},
	{"from_route": "/newsletters", "to_route": "Newsletter"},
	{"from_route": "/profile", "to_route": "me"},
	{"from_route": "/app/<path:app_path>", "to_route": "app"},
]

website_redirects = [
	{"source": r"/desk(.*)", "target": r"/app\1"},
]

base_template = "templates/base.html"

write_file_keys = ["file_url", "file_name"]

notification_config = "vmraid.core.notifications.get_notification_config"

before_tests = "vmraid.utils.install.before_tests"

email_append_to = ["Event", "ToDo", "Communication"]

get_rooms = 'vmraid.chat.doctype.chat_room.chat_room.get_rooms'

calendars = ["Event"]

leaderboards = "vmraid.desk.leaderboard.get_leaderboards"

# login

on_session_creation = [
	"vmraid.core.doctype.activity_log.feed.login_feed",
	"vmraid.core.doctype.user.user.notify_admin_access_to_system_manager"
]

on_logout = "vmraid.core.doctype.session_default_settings.session_default_settings.clear_session_defaults"

# permissions

permission_query_conditions = {
	"Event": "vmraid.desk.doctype.event.event.get_permission_query_conditions",
	"ToDo": "vmraid.desk.doctype.todo.todo.get_permission_query_conditions",
	"User": "vmraid.core.doctype.user.user.get_permission_query_conditions",
	"Dashboard Settings": "vmraid.desk.doctype.dashboard_settings.dashboard_settings.get_permission_query_conditions",
	"Notification Log": "vmraid.desk.doctype.notification_log.notification_log.get_permission_query_conditions",
	"Dashboard": "vmraid.desk.doctype.dashboard.dashboard.get_permission_query_conditions",
	"Dashboard Chart": "vmraid.desk.doctype.dashboard_chart.dashboard_chart.get_permission_query_conditions",
	"Number Card": "vmraid.desk.doctype.number_card.number_card.get_permission_query_conditions",
	"Notification Settings": "vmraid.desk.doctype.notification_settings.notification_settings.get_permission_query_conditions",
	"Note": "vmraid.desk.doctype.note.note.get_permission_query_conditions",
	"Kanban Board": "vmraid.desk.doctype.kanban_board.kanban_board.get_permission_query_conditions",
	"Contact": "vmraid.contacts.address_and_contact.get_permission_query_conditions_for_contact",
	"Address": "vmraid.contacts.address_and_contact.get_permission_query_conditions_for_address",
	"Communication": "vmraid.core.doctype.communication.communication.get_permission_query_conditions_for_communication",
	"Workflow Action": "vmraid.workflow.doctype.workflow_action.workflow_action.get_permission_query_conditions",
	"Prepared Report": "vmraid.core.doctype.prepared_report.prepared_report.get_permission_query_condition"
}

has_permission = {
	"Event": "vmraid.desk.doctype.event.event.has_permission",
	"ToDo": "vmraid.desk.doctype.todo.todo.has_permission",
	"User": "vmraid.core.doctype.user.user.has_permission",
	"Note": "vmraid.desk.doctype.note.note.has_permission",
	"Dashboard Chart": "vmraid.desk.doctype.dashboard_chart.dashboard_chart.has_permission",
	"Number Card": "vmraid.desk.doctype.number_card.number_card.has_permission",
	"Kanban Board": "vmraid.desk.doctype.kanban_board.kanban_board.has_permission",
	"Contact": "vmraid.contacts.address_and_contact.has_permission",
	"Address": "vmraid.contacts.address_and_contact.has_permission",
	"Communication": "vmraid.core.doctype.communication.communication.has_permission",
	"Workflow Action": "vmraid.workflow.doctype.workflow_action.workflow_action.has_permission",
	"File": "vmraid.core.doctype.file.file.has_permission",
	"Prepared Report": "vmraid.core.doctype.prepared_report.prepared_report.has_permission"
}

has_website_permission = {
	"Address": "vmraid.contacts.doctype.address.address.has_website_permission"
}

jinja = {
	"methods": "vmraid.utils.jinja_globals",
	"filters": [
		"vmraid.utils.data.global_date_format",
		"vmraid.utils.markdown",
		"vmraid.website.utils.get_shade",
		"vmraid.website.utils.abs_url",
	]
}

standard_queries = {
	"User": "vmraid.core.doctype.user.user.user_query"
}

doc_events = {
	"*": {
		"after_insert": [
			"vmraid.event_streaming.doctype.event_update_log.event_update_log.notify_consumers"
		],
		"on_update": [
			"vmraid.desk.notifications.clear_doctype_notifications",
			"vmraid.core.doctype.activity_log.feed.update_feed",
			"vmraid.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"vmraid.automation.doctype.assignment_rule.assignment_rule.apply",
			"vmraid.core.doctype.file.file.attach_files_to_document",
			"vmraid.event_streaming.doctype.event_update_log.event_update_log.notify_consumers",
			"vmraid.automation.doctype.assignment_rule.assignment_rule.update_due_date",
			"vmraid.core.doctype.user_type.user_type.apply_permissions_for_non_standard_user_type"
		],
		"after_rename": "vmraid.desk.notifications.clear_doctype_notifications",
		"on_cancel": [
			"vmraid.desk.notifications.clear_doctype_notifications",
			"vmraid.workflow.doctype.workflow_action.workflow_action.process_workflow_actions"
		],
		"on_trash": [
			"vmraid.desk.notifications.clear_doctype_notifications",
			"vmraid.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"vmraid.event_streaming.doctype.event_update_log.event_update_log.notify_consumers"
		],
		"on_change": [
			"vmraid.social.doctype.energy_point_rule.energy_point_rule.process_energy_points",
			"vmraid.automation.doctype.milestone_tracker.milestone_tracker.evaluate_milestone"
		]
	},
	"Event": {
		"after_insert": "vmraid.integrations.doctype.google_calendar.google_calendar.insert_event_in_google_calendar",
		"on_update": "vmraid.integrations.doctype.google_calendar.google_calendar.update_event_in_google_calendar",
		"on_trash": "vmraid.integrations.doctype.google_calendar.google_calendar.delete_event_from_google_calendar",
	},
	"Contact": {
		"after_insert": "vmraid.integrations.doctype.google_contacts.google_contacts.insert_contacts_to_google_contacts",
		"on_update": "vmraid.integrations.doctype.google_contacts.google_contacts.update_contacts_to_google_contacts",
	},
	"DocType": {
		"after_insert": "vmraid.cache_manager.build_domain_restriced_doctype_cache",
		"after_save": "vmraid.cache_manager.build_domain_restriced_doctype_cache",
	},
	"Page": {
		"after_insert": "vmraid.cache_manager.build_domain_restriced_page_cache",
		"after_save": "vmraid.cache_manager.build_domain_restriced_page_cache",
	}
}

scheduler_events = {
	"cron": {
		"0/15 * * * *": [
			"vmraid.oauth.delete_oauth2_data",
			"vmraid.website.doctype.web_page.web_page.check_publish_status",
			"vmraid.twofactor.delete_all_barcodes_for_users"
		]
	},
	"all": [
		"vmraid.email.queue.flush",
		"vmraid.email.doctype.email_account.email_account.pull",
		"vmraid.email.doctype.email_account.email_account.notify_unreplied",
		"vmraid.integrations.doctype.razorpay_settings.razorpay_settings.capture_payment",
		'vmraid.utils.global_search.sync_global_search',
		"vmraid.monitor.flush",
	],
	"hourly": [
		"vmraid.model.utils.link_count.update_link_count",
		'vmraid.model.utils.user_settings.sync_user_settings',
		"vmraid.utils.error.collect_error_snapshots",
		"vmraid.desk.page.backups.backups.delete_downloadable_backups",
		"vmraid.deferred_insert.save_to_db",
		"vmraid.desk.form.document_follow.send_hourly_updates",
		"vmraid.integrations.doctype.google_calendar.google_calendar.sync",
		"vmraid.email.doctype.newsletter.newsletter.send_scheduled_email"
	],
	"daily": [
		"vmraid.email.queue.set_expiry_for_email_queue",
		"vmraid.desk.notifications.clear_notifications",
		"vmraid.core.doctype.error_log.error_log.set_old_logs_as_seen",
		"vmraid.desk.doctype.event.event.send_event_digest",
		"vmraid.sessions.clear_expired_sessions",
		"vmraid.email.doctype.notification.notification.trigger_daily_alerts",
		"vmraid.utils.scheduler.restrict_scheduler_events_if_dormant",
		"vmraid.email.doctype.auto_email_report.auto_email_report.send_daily",
		"vmraid.website.doctype.personal_data_deletion_request.personal_data_deletion_request.remove_unverified_record",
		"vmraid.desk.form.document_follow.send_daily_updates",
		"vmraid.social.doctype.energy_point_settings.energy_point_settings.allocate_review_points",
		"vmraid.integrations.doctype.google_contacts.google_contacts.sync",
		"vmraid.automation.doctype.auto_repeat.auto_repeat.make_auto_repeat_entry",
		"vmraid.automation.doctype.auto_repeat.auto_repeat.set_auto_repeat_as_completed",
		"vmraid.email.doctype.unhandled_email.unhandled_email.remove_old_unhandled_emails",
		"vmraid.core.doctype.prepared_report.prepared_report.delete_expired_prepared_reports",
		"vmraid.core.doctype.log_settings.log_settings.run_log_clean_up"
	],
	"daily_long": [
		"vmraid.integrations.doctype.dropbox_settings.dropbox_settings.take_backups_daily",
		"vmraid.utils.change_log.check_for_update",
		"vmraid.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_daily",
		"vmraid.integrations.doctype.google_drive.google_drive.daily_backup"
	],
	"weekly_long": [
		"vmraid.integrations.doctype.dropbox_settings.dropbox_settings.take_backups_weekly",
		"vmraid.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_weekly",
		"vmraid.desk.doctype.route_history.route_history.flush_old_route_records",
		"vmraid.desk.form.document_follow.send_weekly_updates",
		"vmraid.social.doctype.energy_point_log.energy_point_log.send_weekly_summary",
		"vmraid.integrations.doctype.google_drive.google_drive.weekly_backup"
	],
	"monthly": [
		"vmraid.email.doctype.auto_email_report.auto_email_report.send_monthly",
		"vmraid.social.doctype.energy_point_log.energy_point_log.send_monthly_summary"
	],
	"monthly_long": [
		"vmraid.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_monthly"
	]
}

get_translated_dict = {
	("doctype", "System Settings"): "vmraid.geo.country_info.get_translated_dict",
	("page", "setup-wizard"): "vmraid.geo.country_info.get_translated_dict"
}

sounds = [
	{"name": "email", "src": "/assets/vmraid/sounds/email.mp3", "volume": 0.1},
	{"name": "submit", "src": "/assets/vmraid/sounds/submit.mp3", "volume": 0.1},
	{"name": "cancel", "src": "/assets/vmraid/sounds/cancel.mp3", "volume": 0.1},
	{"name": "delete", "src": "/assets/vmraid/sounds/delete.mp3", "volume": 0.05},
	{"name": "click", "src": "/assets/vmraid/sounds/click.mp3", "volume": 0.05},
	{"name": "error", "src": "/assets/vmraid/sounds/error.mp3", "volume": 0.1},
	{"name": "alert", "src": "/assets/vmraid/sounds/alert.mp3", "volume": 0.2},
	# {"name": "chime", "src": "/assets/vmraid/sounds/chime.mp3"},

	# vmraid.chat sounds
	{ "name": "chat-message", 	   "src": "/assets/vmraid/sounds/chat-message.mp3",      "volume": 0.1 },
	{ "name": "chat-notification", "src": "/assets/vmraid/sounds/chat-notification.mp3", "volume": 0.1 }
	# vmraid.chat sounds
]

bot_parsers = [
	'vmraid.utils.bot.ShowNotificationBot',
	'vmraid.utils.bot.GetOpenListBot',
	'vmraid.utils.bot.ListBot',
	'vmraid.utils.bot.FindBot',
	'vmraid.utils.bot.CountBot'
]

setup_wizard_exception = [
	"vmraid.desk.page.setup_wizard.setup_wizard.email_setup_wizard_exception",
	"vmraid.desk.page.setup_wizard.setup_wizard.log_setup_wizard_exception"
]

before_migrate = ['vmraid.patches.v11_0.sync_user_permission_doctype_before_migrate.execute']
after_migrate = ['vmraid.website.doctype.website_theme.website_theme.after_migrate']

otp_methods = ['OTP App','Email','SMS']

user_data_fields = [
	{"doctype": "Access Log", "strict": True},
	{"doctype": "Activity Log", "strict": True},
	{"doctype": "Comment", "strict": True},
	{
		"doctype": "Contact",
		"filter_by": "email_id",
		"redact_fields": ["first_name", "last_name", "phone", "mobile_no"],
		"rename": True,
	},
	{"doctype": "Contact Email", "filter_by": "email_id"},
	{
		"doctype": "Address",
		"filter_by": "email_id",
		"redact_fields": [
			"address_title",
			"address_line1",
			"address_line2",
			"city",
			"county",
			"state",
			"pincode",
			"phone",
			"fax",
		],
	},
	{
		"doctype": "Communication",
		"filter_by": "sender",
		"redact_fields": ["sender_full_name", "phone_no", "content"],
	},
	{"doctype": "Communication", "filter_by": "recipients"},
	{"doctype": "Email Group Member", "filter_by": "email"},
	{"doctype": "Email Unsubscribe", "filter_by": "email", "partial": True},
	{"doctype": "Email Queue", "filter_by": "sender"},
	{"doctype": "Email Queue Recipient", "filter_by": "recipient"},
	{
		"doctype": "File",
		"filter_by": "attached_to_name",
		"redact_fields": ["file_name", "file_url"],
	},
	{
		"doctype": "User",
		"filter_by": "name",
		"redact_fields": [
			"email",
			"username",
			"first_name",
			"middle_name",
			"last_name",
			"full_name",
			"birth_date",
			"user_image",
			"phone",
			"mobile_no",
			"location",
			"banner_image",
			"interest",
			"bio",
			"email_signature",
		],
	},
	{"doctype": "Version", "strict": True},
]

global_search_doctypes = {
	"Default": [
		{"doctype": "Contact"},
		{"doctype": "Address"},
		{"doctype": "ToDo"},
		{"doctype": "Note"},
		{"doctype": "Event"},
		{"doctype": "Blog Post"},
		{"doctype": "Dashboard"},
		{"doctype": "Country"},
		{"doctype": "Currency"},
		{"doctype": "Newsletter"},
		{"doctype": "Letter Head"},
		{"doctype": "Workflow"},
		{"doctype": "Web Page"},
		{"doctype": "Web Form"}
	]
}
