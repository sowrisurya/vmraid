# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid, json
import vmraid.desk.form.meta
import vmraid.desk.form.load
from vmraid.desk.form.document_follow import follow_document
from vmraid.utils.file_manager import extract_images_from_html

from vmraid import _
from six import string_types

@vmraid.whitelist()
def remove_attach():
	"""remove attachment"""
	fid = vmraid.form_dict.get('fid')
	file_name = vmraid.form_dict.get('file_name')
	vmraid.delete_doc('File', fid)

@vmraid.whitelist()
def validate_link():
	"""validate link when updated by user"""
	import vmraid
	import vmraid.utils

	value, options, fetch = vmraid.form_dict.get('value'), vmraid.form_dict.get('options'), vmraid.form_dict.get('fetch')

	# no options, don't validate
	if not options or options=='null' or options=='undefined':
		vmraid.response['message'] = 'Ok'
		return

	valid_value = vmraid.db.get_all(options, filters=dict(name=value), as_list=1, limit=1)

	if valid_value:
		valid_value = valid_value[0][0]

		# get fetch values
		if fetch:
			# escape with "`"
			fetch = ", ".join(("`{0}`".format(f.strip()) for f in fetch.split(",")))
			fetch_value = None
			try:
				fetch_value = vmraid.db.sql("select %s from `tab%s` where name=%s"
					% (fetch, options, '%s'), (value,))[0]
			except Exception as e:
				error_message = str(e).split("Unknown column '")
				fieldname = None if len(error_message)<=1 else error_message[1].split("'")[0]
				vmraid.msgprint(_("Wrong fieldname <b>{0}</b> in add_fetch configuration of custom client script").format(fieldname))
				vmraid.errprint(vmraid.get_traceback())

			if fetch_value:
				vmraid.response['fetch_values'] = [vmraid.utils.parse_val(c) for c in fetch_value]

		vmraid.response['valid_value'] = valid_value
		vmraid.response['message'] = 'Ok'


@vmraid.whitelist()
def add_comment(reference_doctype, reference_name, content, comment_email, comment_by):
	"""allow any logged user to post a comment"""
	doc = vmraid.get_doc(dict(
		doctype='Comment',
		reference_doctype=reference_doctype,
		reference_name=reference_name,
		comment_email=comment_email,
		comment_type='Comment',
		comment_by=comment_by
	))
	doc.content = extract_images_from_html(doc, content)
	doc.insert(ignore_permissions=True)

	follow_document(doc.reference_doctype, doc.reference_name, vmraid.session.user)
	return doc.as_dict()

@vmraid.whitelist()
def update_comment(name, content):
	"""allow only owner to update comment"""
	doc = vmraid.get_doc('Comment', name)

	if vmraid.session.user not in ['Administrator', doc.owner]:
		vmraid.throw(_('Comment can only be edited by the owner'), vmraid.PermissionError)

	doc.content = content
	doc.save(ignore_permissions=True)

@vmraid.whitelist()
def get_next(doctype, value, prev, filters=None, sort_order='desc', sort_field='modified'):

	prev = int(prev)
	if not filters: filters = []
	if isinstance(filters, string_types):
		filters = json.loads(filters)

	# # condition based on sort order
	condition = ">" if sort_order.lower() == "asc" else "<"

	# switch the condition
	if prev:
		sort_order = "asc" if sort_order.lower() == "desc" else "desc"
		condition = "<" if condition == ">" else ">"

	# # add condition for next or prev item
	filters.append([doctype, sort_field, condition, vmraid.get_value(doctype, value, sort_field)])

	res = vmraid.get_list(doctype,
		fields = ["name"],
		filters = filters,
		order_by = "`tab{0}`.{1}".format(doctype, sort_field) + " " + sort_order,
		limit_start=0, limit_page_length=1, as_list=True)

	if not res:
		vmraid.msgprint(_("No further records"))
		return None
	else:
		return res[0][0]

def get_pdf_link(doctype, docname, print_format='Standard', no_letterhead=0):
	return '/api/method/vmraid.utils.print_format.download_pdf?doctype={doctype}&name={docname}&format={print_format}&no_letterhead={no_letterhead}'.format(
		doctype = doctype,
		docname = docname,
		print_format = print_format,
		no_letterhead = no_letterhead
	)
