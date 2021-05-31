from __future__ import unicode_literals
from vmraid.model.utils.user_settings import update_user_settings
import vmraid, json
from six import iteritems


def execute():
	if vmraid.db.table_exists("__ListSettings"):
		for us in vmraid.db.sql('''select user, doctype, data from __ListSettings''', as_dict=True):
			try:
				data = json.loads(us.data)
			except:
				continue

			if 'List' in data:
				continue

			if 'limit' in data:
				data['page_length'] = data['limit']
				del data['limit']

			new_data = dict(List=data)
			new_data = json.dumps(new_data)

			vmraid.db.sql('''update __ListSettings
				set data=%(new_data)s
				where user=%(user)s
				and doctype=%(doctype)s''',
				{'new_data': new_data, 'user': us.user, 'doctype': us.doctype})

		vmraid.db.sql("RENAME TABLE __ListSettings to __UserSettings")
	else:
		if not vmraid.db.table_exists("__UserSettings"):
			vmraid.db.create_user_settings_table()

		for user in vmraid.db.get_all('User', {'user_type': 'System User'}):
			defaults = vmraid.defaults.get_defaults_for(user.name)
			for key, value in iteritems(defaults):
				if key.startswith('_list_settings:'):
					doctype = key.replace('_list_settings:', '')
					columns = ['`tab{1}`.`{0}`'.format(*c) for c in json.loads(value)]
					for col in columns:
						if "name as" in col:
							columns.remove(col)

					update_user_settings(doctype, {'fields': columns})