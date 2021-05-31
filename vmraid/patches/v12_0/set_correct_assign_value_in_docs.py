import vmraid

def execute():
	vmraid.reload_doc('desk', 'doctype', 'todo')

	query = '''
		SELECT
			name, reference_type, reference_name, {} as assignees
		FROM
			`tabToDo`
		WHERE
			COALESCE(reference_type, '') != '' AND
			COALESCE(reference_name, '') != '' AND
			status != 'Cancelled'
		GROUP BY
			reference_type, reference_name
	'''

	assignments = vmraid.db.multisql({
		'mariadb': query.format('GROUP_CONCAT(DISTINCT `owner`)'),
		'postgres': query.format('STRING_AGG(DISTINCT "owner", ",")')
	}, as_dict=True)

	for doc in assignments:
		assignments = doc.assignees.split(',')
		vmraid.db.set_value(
			doc.reference_type,
			doc.reference_name,
			'_assign',
			vmraid.as_json(assignments),
			update_modified=False
		)
