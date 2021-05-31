# -*- coding: utf-8 -*-
# Copyright (c) 2017, VMRaid Technologies and contributors
# For license information, please see license.txt

import os

import vmraid
import vmraid.modules.import_file
from vmraid import _
from vmraid.core.doctype.data_import_legacy.importer import upload
from vmraid.model.document import Document
from vmraid.modules.import_file import import_file_by_path as _import_file_by_path
from vmraid.utils.background_jobs import enqueue
from vmraid.utils.data import format_datetime


class DataImportLegacy(Document):
	def autoname(self):
		if not self.name:
			self.name = "Import on " + format_datetime(self.creation)

	def validate(self):
		if not self.import_file:
			self.db_set("total_rows", 0)
		if self.import_status == "In Progress":
			vmraid.throw(_("Can't save the form as data import is in progress."))

		# validate the template just after the upload
		# if there is total_rows in the doc, it means that the template is already validated and error free
		if self.import_file and not self.total_rows:
			upload(data_import_doc=self, from_data_import="Yes", validate_template=True)


@vmraid.whitelist()
def get_importable_doctypes():
	return vmraid.cache().hget("can_import", vmraid.session.user)


@vmraid.whitelist()
def import_data(data_import):
	vmraid.db.set_value("Data Import Legacy", data_import, "import_status", "In Progress", update_modified=False)
	vmraid.publish_realtime("data_import_progress", {"progress": "0",
		"data_import": data_import, "reload": True}, user=vmraid.session.user)

	from vmraid.core.page.background_jobs.background_jobs import get_info
	enqueued_jobs = [d.get("job_name") for d in get_info()]

	if data_import not in enqueued_jobs:
		enqueue(upload, queue='default', timeout=6000, event='data_import', job_name=data_import,
			data_import_doc=data_import, from_data_import="Yes", user=vmraid.session.user)


def import_doc(path, overwrite=False, ignore_links=False, ignore_insert=False,
	insert=False, submit=False, pre_process=None):
	if os.path.isdir(path):
		files = [os.path.join(path, f) for f in os.listdir(path)]
	else:
		files = [path]

	for f in files:
		if f.endswith(".json"):
			vmraid.flags.mute_emails = True
			_import_file_by_path(f, data_import=True, force=True, pre_process=pre_process, reset_permissions=True)
			vmraid.flags.mute_emails = False
			vmraid.db.commit()
		elif f.endswith(".csv"):
			import_file_by_path(f, ignore_links=ignore_links, overwrite=overwrite, submit=submit, pre_process=pre_process)
			vmraid.db.commit()


def import_file_by_path(path, ignore_links=False, overwrite=False, submit=False, pre_process=None, no_email=True):
	from vmraid.utils.csvutils import read_csv_content
	print("Importing " + path)
	with open(path, "r") as infile:
		upload(rows=read_csv_content(infile.read()), ignore_links=ignore_links, no_email=no_email, overwrite=overwrite,
			submit_after_import=submit, pre_process=pre_process)


def export_json(doctype, path, filters=None, or_filters=None, name=None, order_by="creation asc"):
	def post_process(out):
		del_keys = ('modified_by', 'creation', 'owner', 'idx')
		for doc in out:
			for key in del_keys:
				if key in doc:
					del doc[key]
			for k, v in doc.items():
				if isinstance(v, list):
					for child in v:
						for key in del_keys + ('docstatus', 'doctype', 'modified', 'name'):
							if key in child:
								del child[key]

	out = []
	if name:
		out.append(vmraid.get_doc(doctype, name).as_dict())
	elif vmraid.db.get_value("DocType", doctype, "issingle"):
		out.append(vmraid.get_doc(doctype).as_dict())
	else:
		for doc in vmraid.get_all(doctype, fields=["name"], filters=filters, or_filters=or_filters, limit_page_length=0, order_by=order_by):
			out.append(vmraid.get_doc(doctype, doc.name).as_dict())
	post_process(out)

	dirname = os.path.dirname(path)
	if not os.path.exists(dirname):
		path = os.path.join('..', path)

	with open(path, "w") as outfile:
		outfile.write(vmraid.as_json(out))


def export_csv(doctype, path):
	from vmraid.core.doctype.data_export.exporter import export_data
	with open(path, "wb") as csvfile:
		export_data(doctype=doctype, all_doctypes=True, template=True, with_data=True)
		csvfile.write(vmraid.response.result.encode("utf-8"))


@vmraid.whitelist()
def export_fixture(doctype, app):
	if vmraid.session.user != "Administrator":
		raise vmraid.PermissionError

	if not os.path.exists(vmraid.get_app_path(app, "fixtures")):
		os.mkdir(vmraid.get_app_path(app, "fixtures"))

	export_json(doctype, vmraid.get_app_path(app, "fixtures", vmraid.scrub(doctype) + ".json"), order_by="name asc")
