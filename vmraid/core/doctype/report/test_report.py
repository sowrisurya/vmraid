# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# See license.txt

from __future__ import unicode_literals
import vmraid, json, os
import unittest
from vmraid.desk.query_report import run, save_report
from vmraid.custom.doctype.customize_form.customize_form import reset_customization

test_records = vmraid.get_test_records('Report')
test_dependencies = ['User']

class TestReport(unittest.TestCase):
	def test_report_builder(self):
		if vmraid.db.exists('Report', 'User Activity Report'):
			vmraid.delete_doc('Report', 'User Activity Report')

		with open(os.path.join(os.path.dirname(__file__), 'user_activity_report.json'), 'r') as f:
			vmraid.get_doc(json.loads(f.read())).insert()

		report = vmraid.get_doc('Report', 'User Activity Report')
		columns, data = report.get_data()
		self.assertEqual(columns[0].get('label'), 'ID')
		self.assertEqual(columns[1].get('label'), 'User Type')
		self.assertTrue('Administrator' in [d[0] for d in data])

	def test_query_report(self):
		report = vmraid.get_doc('Report', 'Permitted Documents For User')
		columns, data = report.get_data(filters={'user': 'Administrator', 'doctype': 'DocType'})
		self.assertEqual(columns[0].get('label'), 'Name')
		self.assertEqual(columns[1].get('label'), 'Module')
		self.assertTrue('User' in [d.get('name') for d in data])

	def test_custom_report(self):
		reset_customization('User')
		custom_report_name = save_report(
			'Permitted Documents For User',
			'Permitted Documents For User Custom',
			json.dumps([{
				'fieldname': 'email',
				'fieldtype': 'Data',
				'label': 'Email',
				'insert_after_index': 0,
				'link_field': 'name',
				'doctype': 'User',
				'options': 'Email',
				'width': 100,
				'id':'email',
				'name': 'Email'
			}]))
		custom_report = vmraid.get_doc('Report', custom_report_name)
		columns, result = custom_report.run_query_report(
			filters={
				'user': 'Administrator',
				'doctype': 'User'
			}, user=vmraid.session.user)

		self.assertListEqual(['email'], [column.get('fieldname') for column in columns])
		admin_dict = vmraid.core.utils.find(result, lambda d: d['name'] == 'Administrator')
		self.assertDictEqual({'name': 'Administrator', 'user_type': 'System User', 'email': 'admin@example.com'}, admin_dict)

	def test_report_with_custom_column(self):
		reset_customization('User')
		response = run('Permitted Documents For User',
			filters={'user': 'Administrator', 'doctype': 'User'},
			custom_columns=[{
				'fieldname': 'email',
				'fieldtype': 'Data',
				'label': 'Email',
				'insert_after_index': 0,
				'link_field': 'name',
				'doctype': 'User',
				'options': 'Email',
				'width': 100,
				'id':'email',
				'name': 'Email'
			}])
		result = response.get('result')
		columns = response.get('columns')
		self.assertListEqual(['name', 'email', 'user_type'], [column.get('fieldname') for column in columns])
		admin_dict = vmraid.core.utils.find(result, lambda d: d['name'] == 'Administrator')
		self.assertDictEqual({'name': 'Administrator', 'user_type': 'System User', 'email': 'admin@example.com'}, admin_dict)

	def test_report_permissions(self):
		vmraid.set_user('test@example.com')
		vmraid.db.sql("""delete from `tabHas Role` where parent = %s
			and role = 'Test Has Role'""", vmraid.session.user, auto_commit=1)

		if not vmraid.db.exists('Role', 'Test Has Role'):
			role = vmraid.get_doc({
				'doctype': 'Role',
				'role_name': 'Test Has Role'
			}).insert(ignore_permissions=True)

		if not vmraid.db.exists("Report", "Test Report"):
			report = vmraid.get_doc({
				'doctype': 'Report',
				'ref_doctype': 'User',
				'report_name': 'Test Report',
				'report_type': 'Query Report',
				'is_standard': 'No',
				'roles': [
					{'role': 'Test Has Role'}
				]
			}).insert(ignore_permissions=True)
		else:
			report = vmraid.get_doc('Report', 'Test Report')

		self.assertNotEqual(report.is_permitted(), True)
		vmraid.set_user('Administrator')

	# test for the `_format` method if report data doesn't have sort_by parameter
	def test_format_method(self):
		if vmraid.db.exists('Report', 'User Activity Report Without Sort'):
			vmraid.delete_doc('Report', 'User Activity Report Without Sort')
		with open(os.path.join(os.path.dirname(__file__), 'user_activity_report_without_sort.json'), 'r') as f:
			vmraid.get_doc(json.loads(f.read())).insert()

		report = vmraid.get_doc('Report', 'User Activity Report Without Sort')
		columns, data = report.get_data()

		self.assertEqual(columns[0].get('label'), 'ID')
		self.assertEqual(columns[1].get('label'), 'User Type')
		self.assertTrue('Administrator' in [d[0] for d in data])
		vmraid.delete_doc('Report', 'User Activity Report Without Sort')

	def test_non_standard_script_report(self):
		report_name = 'Test Non Standard Script Report'
		if not vmraid.db.exists("Report", report_name):
			report = vmraid.get_doc({
				'doctype': 'Report',
				'ref_doctype': 'User',
				'report_name': report_name,
				'report_type': 'Script Report',
				'is_standard': 'No',
			}).insert(ignore_permissions=True)
		else:
			report = vmraid.get_doc('Report', report_name)

		report.report_script = '''
totals = {}
for user in vmraid.get_all('User', fields = ['name', 'user_type', 'creation']):
	if not user.user_type in totals:
		totals[user.user_type] = 0
	totals[user.user_type] = totals[user.user_type] + 1

data = [
	[
		{'fieldname': 'type', 'label': 'Type'},
		{'fieldname': 'value', 'label': 'Value'}
	],
	[
		{"type":key, "value": value} for key, value in totals.items()
	]
]
'''
		report.save()
		data = report.get_data()

		# check columns
		self.assertEqual(data[0][0]['label'], 'Type')

		# check values
		self.assertTrue('System User' in [d.get('type') for d in data[1]])

	def test_script_report_with_columns(self):
		report_name = 'Test Script Report With Columns'

		if vmraid.db.exists("Report", report_name):
			vmraid.delete_doc('Report', report_name)

		report = vmraid.get_doc({
			'doctype': 'Report',
			'ref_doctype': 'User',
			'report_name': report_name,
			'report_type': 'Script Report',
			'is_standard': 'No',
			'columns': [
				dict(fieldname='type', label='Type', fieldtype='Data'),
				dict(fieldname='value', label='Value', fieldtype='Int'),
			]
		}).insert(ignore_permissions=True)

		report.report_script = '''
totals = {}
for user in vmraid.get_all('User', fields = ['name', 'user_type', 'creation']):
	if not user.user_type in totals:
		totals[user.user_type] = 0
	totals[user.user_type] = totals[user.user_type] + 1

result = [
		{"type":key, "value": value} for key, value in totals.items()
	]
'''

		report.save()
		data = report.get_data()

		# check columns
		self.assertEqual(data[0][0]['label'], 'Type')

		# check values
		self.assertTrue('System User' in [d.get('type') for d in data[1]])

	def test_toggle_disabled(self):
		"""Make sure that authorization is respected.
		"""
		# Assuming that there will be reports in the system.
		reports = vmraid.get_all(doctype='Report', limit=1)
		report_name = reports[0]['name']
		doc = vmraid.get_doc('Report', report_name)
		status = doc.disabled

		# User has write permission on reports and should pass through
		vmraid.set_user('test@example.com')
		doc.toggle_disable(not status)
		doc.reload()
		self.assertNotEqual(status, doc.disabled)

		# User has no write permission on reports, permission error is expected.
		vmraid.set_user('test1@example.com')
		doc = vmraid.get_doc('Report', report_name)
		with self.assertRaises(vmraid.exceptions.ValidationError):
			doc.toggle_disable(1)

		# Set user back to administrator
		vmraid.set_user('Administrator')
