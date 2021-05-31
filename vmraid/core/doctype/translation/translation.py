# -*- coding: utf-8 -*-
# Copyright (c) 2015, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.model.document import Document
from vmraid.utils import strip_html_tags, is_html
from vmraid.translate import get_translator_url
import json

class Translation(Document):
	def validate(self):
		if is_html(self.source_text):
			self.remove_html_from_source()

	def remove_html_from_source(self):
		self.source_text = strip_html_tags(self.source_text).strip()

	def on_update(self):
		clear_user_translation_cache(self.language)

	def on_trash(self):
		clear_user_translation_cache(self.language)

	def contribute(self):
		pass

	def get_contribution_status(self):
		pass

@vmraid.whitelist()
def create_translations(translation_map, language):
	from vmraid.vmraidclient import VMRaidClient

	translation_map = json.loads(translation_map)
	translation_map_to_send = vmraid._dict({})
	# first create / update local user translations
	for source_id, translation_dict in translation_map.items():
		translation_dict = vmraid._dict(translation_dict)
		existing_doc_name = vmraid.db.get_all('Translation', {
			'source_text': translation_dict.source_text,
			'context': translation_dict.context or '',
			'language': language,
		})
		translation_map_to_send[source_id] = translation_dict
		if existing_doc_name:
			vmraid.db.set_value('Translation', existing_doc_name[0].name, {
				'translated_text': translation_dict.translated_text,
				'contributed': 1,
				'contribution_status': 'Pending'
			})
			translation_map_to_send[source_id].name = existing_doc_name[0].name
		else:
			doc = vmraid.get_doc({
				'doctype': 'Translation',
				'source_text': translation_dict.source_text,
				'contributed': 1,
				'contribution_status': 'Pending',
				'translated_text': translation_dict.translated_text,
				'context': translation_dict.context,
				'language': language
			})
			doc.insert()
			translation_map_to_send[source_id].name = doc.name

	params = {
		'language': language,
		'contributor_email': vmraid.session.user,
		'contributor_name': vmraid.utils.get_fullname(vmraid.session.user),
		'translation_map': json.dumps(translation_map_to_send)
	}

	translator = VMRaidClient(get_translator_url())
	added_translations = translator.post_api('translator.api.add_translations', params=params)

	for local_docname, remote_docname in added_translations.items():
		vmraid.db.set_value('Translation', local_docname, 'contribution_docname', remote_docname)

def clear_user_translation_cache(lang):
	vmraid.cache().hdel('lang_user_translations', lang)
