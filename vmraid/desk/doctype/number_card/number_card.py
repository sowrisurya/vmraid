# -*- coding: utf-8 -*-
# Copyright (c) 2020, VMRaid Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.model.document import Document
from vmraid.utils import cint
from vmraid.model.naming import append_number_if_name_exists
from vmraid.modules.export_file import export_to_files
from vmraid.config import get_modules_from_all_apps_for_user

class NumberCard(Document):
	def autoname(self):
		if not self.name:
			self.name = self.label

		if vmraid.db.exists("Number Card", self.name):
			self.name = append_number_if_name_exists('Number Card', self.name)

	def on_update(self):
		if vmraid.conf.developer_mode and self.is_standard:
			export_to_files(record_list=[['Number Card', self.name]], record_module=self.module)

def get_permission_query_conditions(user=None):
	if not user:
		user = vmraid.session.user

	if user == 'Administrator':
		return

	roles = vmraid.get_roles(user)
	if "System Manager" in roles:
		return None

	doctype_condition = False
	module_condition = False

	allowed_doctypes = [vmraid.db.escape(doctype) for doctype in vmraid.permissions.get_doctypes_with_read()]
	allowed_modules = [vmraid.db.escape(module.get('module_name')) for module in get_modules_from_all_apps_for_user()]

	if allowed_doctypes:
		doctype_condition = '`tabNumber Card`.`document_type` in ({allowed_doctypes})'.format(
			allowed_doctypes=','.join(allowed_doctypes))
	if allowed_modules:
		module_condition =  '''`tabNumber Card`.`module` in ({allowed_modules})
			or `tabNumber Card`.`module` is NULL'''.format(
			allowed_modules=','.join(allowed_modules))

	return '''
		{doctype_condition}
		and
		{module_condition}
	'''.format(doctype_condition=doctype_condition, module_condition=module_condition)

def has_permission(doc, ptype, user):
	roles = vmraid.get_roles(user)
	if "System Manager" in roles:
		return True

	allowed_doctypes = tuple(vmraid.permissions.get_doctypes_with_read())
	if doc.document_type in allowed_doctypes:
		return True

	return False

@vmraid.whitelist()
def get_result(doc, filters, to_date=None):
	doc = vmraid.parse_json(doc)
	fields = []
	sql_function_map = {
		'Count': 'count',
		'Sum': 'sum',
		'Average': 'avg',
		'Minimum': 'min',
		'Maximum': 'max'
	}

	function = sql_function_map[doc.function]

	if function == 'count':
		fields = ['{function}(*) as result'.format(function=function)]
	else:
		fields = ['{function}({based_on}) as result'.format(function=function, based_on=doc.aggregate_function_based_on)]

	filters = vmraid.parse_json(filters)

	if not filters:
		filters = []

	if to_date:
		filters.append([doc.document_type, 'creation', '<', to_date])

	res = vmraid.db.get_list(doc.document_type, fields=fields, filters=filters)
	number = res[0]['result'] if res else 0

	return cint(number)

@vmraid.whitelist()
def get_percentage_difference(doc, filters, result):
	doc = vmraid.parse_json(doc)
	result = vmraid.parse_json(result)

	doc = vmraid.get_doc('Number Card', doc.name)

	if not doc.get('show_percentage_stats'):
		return

	previous_result = calculate_previous_result(doc, filters)
	if previous_result == 0:
		return None
	else:
		if result == previous_result:
			return 0
		else:
			return ((result/previous_result)-1)*100.0


def calculate_previous_result(doc, filters):
	from vmraid.utils import add_to_date

	current_date = vmraid.utils.now()
	if doc.stats_time_interval == 'Daily':
		previous_date = add_to_date(current_date, days=-1)
	elif doc.stats_time_interval == 'Weekly':
		previous_date = add_to_date(current_date, weeks=-1)
	elif doc.stats_time_interval == 'Monthly':
		previous_date = add_to_date(current_date, months=-1)
	else:
		previous_date = add_to_date(current_date, years=-1)

	number = get_result(doc, filters, previous_date)
	return number

@vmraid.whitelist()
def create_number_card(args):
	args = vmraid.parse_json(args)
	doc = vmraid.new_doc('Number Card')

	doc.update(args)
	doc.insert(ignore_permissions=True)
	return doc

@vmraid.whitelist()
@vmraid.validate_and_sanitize_search_inputs
def get_cards_for_user(doctype, txt, searchfield, start, page_len, filters):
	meta = vmraid.get_meta(doctype)
	searchfields = meta.get_search_fields()
	search_conditions = []

	if not vmraid.db.exists('DocType', doctype):
		return

	if txt:
		for field in searchfields:
			search_conditions.append('`tab{doctype}`.`{field}` like %(txt)s'.format(field=field, doctype=doctype, txt=txt))

		search_conditions = ' or '.join(search_conditions)

	search_conditions = 'and (' + search_conditions +')' if search_conditions else ''
	conditions, values = vmraid.db.build_conditions(filters)
	values['txt'] = '%' + txt + '%'

	return vmraid.db.sql(
		'''select
			`tabNumber Card`.name, `tabNumber Card`.label, `tabNumber Card`.document_type
		from
			`tabNumber Card`
		where
			{conditions} and
			(`tabNumber Card`.owner = '{user}' or
			`tabNumber Card`.is_public = 1)
			{search_conditions}
	'''.format(
		filters=filters,
		user=vmraid.session.user,
		search_conditions=search_conditions,
		conditions=conditions
	), values)

@vmraid.whitelist()
def create_report_number_card(args):
	card = create_number_card(args)
	args = vmraid.parse_json(args)
	args.name = card.name
	if args.dashboard:
		add_card_to_dashboard(vmraid.as_json(args))

@vmraid.whitelist()
def add_card_to_dashboard(args):
	args = vmraid.parse_json(args)

	dashboard = vmraid.get_doc('Dashboard', args.dashboard)
	dashboard_link = vmraid.new_doc('Number Card Link')
	dashboard_link.card = args.name

	if args.set_standard and dashboard.is_standard:
		card = vmraid.get_doc('Number Card', dashboard_link.card)
		card.is_standard = 1
		card.module = dashboard.module
		card.save()

	dashboard.append('cards', dashboard_link)
	dashboard.save()
