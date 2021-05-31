# -*- coding: utf-8 -*-
# Copyright (c) 2018, VMRaid Technologies and contributors
# For license information, please see license.txt


from __future__ import unicode_literals

import json

import vmraid
from vmraid.desk.form.load import get_attachments
from vmraid.desk.query_report import generate_report_result
from vmraid.model.document import Document
from vmraid.utils import gzip_compress, gzip_decompress
from vmraid.utils.background_jobs import enqueue
from vmraid.core.doctype.file.file import remove_all


class PreparedReport(Document):
	def before_insert(self):
		self.status = "Queued"
		self.report_start_time = vmraid.utils.now()

	def enqueue_report(self):
		enqueue(run_background, prepared_report=self.name, timeout=6000)



def run_background(prepared_report):
	instance = vmraid.get_doc("Prepared Report", prepared_report)
	report = vmraid.get_doc("Report", instance.ref_report_doctype)

	try:
		report.custom_columns = []

		if report.report_type == "Custom Report":
			custom_report_doc = report
			reference_report = custom_report_doc.reference_report
			report = vmraid.get_doc("Report", reference_report)
			if custom_report_doc.json:
				data = json.loads(custom_report_doc.json)
				if data:
					report.custom_columns = data["columns"]

		result = generate_report_result(
			report=report,
			filters=instance.filters,
			user=instance.owner
		)
		create_json_gz_file(result["result"], "Prepared Report", instance.name)

		instance.status = "Completed"
		instance.columns = json.dumps(result["columns"])
		instance.report_end_time = vmraid.utils.now()
		instance.save(ignore_permissions=True)

	except Exception:
		vmraid.log_error(vmraid.get_traceback())
		instance = vmraid.get_doc("Prepared Report", prepared_report)
		instance.status = "Error"
		instance.error_message = vmraid.get_traceback()
		instance.save(ignore_permissions=True)

	vmraid.publish_realtime(
		"report_generated",
		{
			"report_name": instance.report_name,
			"name": instance.name
		},
		user=vmraid.session.user
	)

@vmraid.whitelist()
def get_reports_in_queued_state(report_name, filters):
	reports = vmraid.get_all('Prepared Report',
		filters = {
			'report_name': report_name,
			'filters': json.dumps(json.loads(filters)),
			'status': 'Queued'
		})
	return reports

def delete_expired_prepared_reports():
	system_settings = vmraid.get_single('System Settings')
	enable_auto_deletion = system_settings.enable_prepared_report_auto_deletion
	if enable_auto_deletion:
		expiry_period = system_settings.prepared_report_expiry_period
		prepared_reports_to_delete = vmraid.get_all('Prepared Report',
			filters = {
				'creation': ['<', vmraid.utils.add_days(vmraid.utils.now(), -expiry_period)]
			})

		batches = vmraid.utils.create_batch(prepared_reports_to_delete, 100)
		for batch in batches:
			args = {
				'reports': batch,
			}
			enqueue(method=delete_prepared_reports, job_name="delete_prepared_reports", **args)

@vmraid.whitelist()
def delete_prepared_reports(reports):
	reports = vmraid.parse_json(reports)
	for report in reports:
		vmraid.delete_doc('Prepared Report', report['name'], ignore_permissions=True, delete_permanently=True)

def create_json_gz_file(data, dt, dn):
	# Storing data in CSV file causes information loss
	# Reports like P&L Statement were completely unsuable because of this
	json_filename = "{0}.json.gz".format(
		vmraid.utils.data.format_datetime(vmraid.utils.now(), "Y-m-d-H:M")
	)
	encoded_content = vmraid.safe_encode(vmraid.as_json(data))
	compressed_content = gzip_compress(encoded_content)

	# Call save() file function to upload and attach the file
	_file = vmraid.get_doc({
		"doctype": "File",
		"file_name": json_filename,
		"attached_to_doctype": dt,
		"attached_to_name": dn,
		"content": compressed_content,
		"is_private": 1
	})
	_file.save(ignore_permissions=True)


@vmraid.whitelist()
def download_attachment(dn):
	attachment = get_attachments("Prepared Report", dn)[0]
	vmraid.local.response.filename = attachment.file_name[:-2]
	attached_file = vmraid.get_doc("File", attachment.name)
	vmraid.local.response.filecontent = gzip_decompress(attached_file.get_content())
	vmraid.local.response.type = "binary"


def get_permission_query_condition(user):
	if not user: user = vmraid.session.user
	if user == "Administrator":
		return None

	from vmraid.utils.user import UserPermissions
	user = UserPermissions(user)

	if "System Manager" in user.roles:
		return None

	reports = [vmraid.db.escape(report) for report in user.get_all_reports().keys()]

	return """`tabPrepared Report`.ref_report_doctype in ({reports})"""\
			.format(reports=','.join(reports))


def has_permission(doc, user):
	if not user: user = vmraid.session.user
	if user == "Administrator":
		return True

	from vmraid.utils.user import UserPermissions
	user = UserPermissions(user)

	if "System Manager" in user.roles:
		return True

	return doc.ref_report_doctype in user.get_all_reports().keys()
