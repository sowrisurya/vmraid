import vmraid
from vmraid.utils import add_to_date, now

@vmraid.whitelist()
def create_if_not_exists(doc):
	'''Create records if they dont exist.
	Will check for uniqueness by checking if a record exists with these field value pairs

	:param doc: dict of field value pairs. can be a list of dict for multiple records.
	'''

	if not vmraid.local.dev_server:
		vmraid.throw('This method can only be accessed in development', vmraid.PermissionError)

	doc = vmraid.parse_json(doc)

	if not isinstance(doc, list):
		docs = [doc]
	else:
		docs = doc

	names = []
	for doc in docs:
		doc = vmraid._dict(doc)
		filters = doc.copy()
		filters.pop('doctype')
		name = vmraid.db.exists(doc.doctype, filters)
		if not name:
			d = vmraid.get_doc(doc)
			d.insert(ignore_permissions=True)
			name = d.name
		names.append(name)

	return names


@vmraid.whitelist()
def create_todo_records():
	if vmraid.db.get_all('ToDo', {'description': 'this is first todo'}):
		return

	vmraid.get_doc({
		"doctype": "ToDo",
		"date": add_to_date(now(), days=7),
		"description": "this is first todo"
	}).insert()
	vmraid.get_doc({
		"doctype": "ToDo",
		"date": add_to_date(now(), days=-7),
		"description": "this is second todo"
	}).insert()
	vmraid.get_doc({
		"doctype": "ToDo",
		"date": add_to_date(now(), months=2),
		"description": "this is third todo"
	}).insert()
	vmraid.get_doc({
		"doctype": "ToDo",
		"date": add_to_date(now(), months=-2),
		"description": "this is fourth todo"
	}).insert()

@vmraid.whitelist()
def setup_workflow():
	from vmraid.workflow.doctype.workflow.test_workflow import create_todo_workflow
	create_todo_workflow()
	create_todo_records()
	vmraid.clear_cache()

@vmraid.whitelist()
def create_contact_phone_nos_records():
	if vmraid.db.get_all('Contact', {'first_name': 'Test Contact'}):
		return

	doc = vmraid.new_doc('Contact')
	doc.first_name = 'Test Contact'
	for index in range(1000):
		doc.append('phone_nos', {'phone': '123456{}'.format(index)})
	doc.insert()

@vmraid.whitelist()
def create_doctype(name, fields):
	fields = vmraid.parse_json(fields)
	if vmraid.db.exists('DocType', name):
		return
	vmraid.get_doc({
		"doctype": "DocType",
		"module": "Core",
		"custom": 1,
		"fields": fields,
		"permissions": [{
			"role": "System Manager",
			"read": 1
		}],
		"name": name
	}).insert()

@vmraid.whitelist()
def create_child_doctype(name, fields):
	fields = vmraid.parse_json(fields)
	if vmraid.db.exists('DocType', name):
		return
	vmraid.get_doc({
		"doctype": "DocType",
		"module": "Core",
		"istable": 1,
		"custom": 1,
		"fields": fields,
		"permissions": [{
			"role": "System Manager",
			"read": 1
		}],
		"name": name
	}).insert()

@vmraid.whitelist()
def create_contact_records():
	if vmraid.db.get_all('Contact', {'first_name': 'Test Form Contact 1'}):
		return

	insert_contact('Test Form Contact 1', '12345')
	insert_contact('Test Form Contact 2', '54321')
	insert_contact('Test Form Contact 3', '12345')


def insert_contact(first_name, phone_number):
	doc = vmraid.get_doc({
		'doctype': 'Contact',
		'first_name': first_name
	})
	doc.append('phone_nos', {'phone': phone_number})
	doc.insert()
