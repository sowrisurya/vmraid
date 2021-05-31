from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.rename_doc('Language', 'zh-cn', 'zh', force=True,
		merge=True if vmraid.db.exists('Language', 'zh') else False)
	if vmraid.db.get_value('Language', 'zh-tw') == 'zh-tw':
		vmraid.rename_doc('Language', 'zh-tw', 'zh-TW', force=True)

	vmraid.db.set_value('Language', 'zh', 'language_code', 'zh')
	vmraid.db.set_value('Language', 'zh-TW', 'language_code', 'zh-TW')