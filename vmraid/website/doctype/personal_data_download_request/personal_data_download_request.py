# -*- coding: utf-8 -*-
# Copyright (c) 2019, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
import json
from vmraid import _
from vmraid.model.document import Document
from vmraid.utils.verified_command import get_signed_params

class PersonalDataDownloadRequest(Document):
	def after_insert(self):
		personal_data = get_user_data(self.user)

		vmraid.enqueue_doc(self.doctype, self.name, 'generate_file_and_send_mail',
			queue='short', personal_data=personal_data, now=vmraid.flags.in_test)

	def generate_file_and_send_mail(self, personal_data):
		"""generate the file link for download"""
		user_name = self.user_name.replace(' ','-')
		f = vmraid.get_doc({
			'doctype': 'File',
			'file_name': 'Personal-Data-'+user_name+'-'+self.name+'.json',
			"attached_to_doctype": 'Personal Data Download Request',
			"attached_to_name": self.name,
			'content': str(personal_data),
			'is_private': 1
		})
		f.save(ignore_permissions=True)

		file_link = vmraid.utils.get_url("/api/method/vmraid.core.doctype.file.file.download_file") +\
			"?" + get_signed_params({"file_url": f.file_url})
		host_name = vmraid.local.site
		vmraid.sendmail(
			recipients=self.user,
			subject=_("Download Your Data"),
			template="download_data",
			args={
				'user': self.user,
				'user_name': self.user_name,
				'link': file_link,
				'host_name': host_name
			},
			header=[_("Download Your Data"), "green"]
		)

def get_user_data(user):
	""" returns user data not linked to User doctype """
	hooks = vmraid.get_hooks("user_data_fields")
	data = {}
	for hook in hooks:
		d = data.get(hook.get("doctype"),[])
		d += vmraid.get_all(hook.get("doctype"), {hook.get("filter_by", "owner"): user}, ["*"])
		if d:
			data.update({ hook.get("doctype"):d })
	return json.dumps(data, indent=2, default=str)