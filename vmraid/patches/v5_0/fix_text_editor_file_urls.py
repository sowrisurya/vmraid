from __future__ import unicode_literals, print_function
import vmraid
import re

def execute():
	"""Fix relative urls for image src="files/" to src="/files/" in DocTypes with text editor fields"""
	doctypes_with_text_fields = vmraid.get_all("DocField", fields=["parent", "fieldname"],
		filters={"fieldtype": "Text Editor"})

	done = []
	for opts in doctypes_with_text_fields:
		if opts in done:
			continue

		try:
			result = vmraid.get_all(opts.parent, fields=["name", opts.fieldname])
		except vmraid.db.SQLError:
			# bypass single tables
			continue

		for data in result:
			old_value = data[opts.fieldname]
			if not old_value:
				continue

			html = scrub_relative_urls(old_value)
			if html != old_value:
				# print_diff(html, old_value)
				vmraid.db.set_value(opts.parent, data.name, opts.fieldname, html, update_modified=False)

		done.append(opts)

def scrub_relative_urls(html):
	"""prepend a slash before a relative url"""
	try:
		return re.sub(r'src[\s]*=[\s]*[\'"]files/([^\'"]*)[\'"]', r'src="/files/\g<1>"', html)
	except:
		print("Error", html)
		raise

def print_diff(html, old_value):
	import difflib
	diff = difflib.unified_diff(old_value.splitlines(1), html.splitlines(1), lineterm='')
	print('\n'.join(list(diff)))
