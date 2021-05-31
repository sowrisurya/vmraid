# -*- coding: utf-8 -*-
# Copyright (c) 2015, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid, json, re
from vmraid import _
from vmraid.model.document import Document

class Language(Document):
	def validate(self):
		validate_with_regex(self.language_code, "Language Code")

	def before_rename(self, old, new, merge=False):
		validate_with_regex(new, "Name")

def validate_with_regex(name, label):
	pattern = re.compile("^[a-zA-Z]+[-_]*[a-zA-Z]+$")
	if not pattern.match(name):
		vmraid.throw(_("""{0} must begin and end with a letter and can only contain letters,
				hyphen or underscore.""").format(label))

def export_languages_json():
	'''Export list of all languages'''
	languages = vmraid.db.get_all('Language', fields=['name', 'language_name'])
	languages = [{'name': d.language_name, 'code': d.name} for d in languages]

	languages.sort(key = lambda a: a['code'])

	with open(vmraid.get_app_path('vmraid', 'geo', 'languages.json'), 'w') as f:
		f.write(vmraid.as_json(languages))

def sync_languages():
	'''Sync vmraid/geo/languages.json with Language'''
	with open(vmraid.get_app_path('vmraid', 'geo', 'languages.json'), 'r') as f:
		data = json.loads(f.read())

	for l in data:
		if not vmraid.db.exists('Language', l['code']):
			vmraid.get_doc({
				'doctype': 'Language',
				'language_code': l['code'],
				'language_name': l['name']
			}).insert()

def update_language_names():
	'''Update vmraid/geo/languages.json names (for use via patch)'''
	with open(vmraid.get_app_path('vmraid', 'geo', 'languages.json'), 'r') as f:
		data = json.loads(f.read())

	for l in data:
		vmraid.db.set_value('Language', l['code'], 'language_name', l['name'])