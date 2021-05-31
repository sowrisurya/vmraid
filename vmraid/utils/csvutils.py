# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid
from vmraid import msgprint, _
import json
import csv
import six
import requests
from six import StringIO, text_type, string_types
from vmraid.utils import encode, cstr, cint, flt, comma_or

def read_csv_content_from_uploaded_file(ignore_encoding=False):
	if getattr(vmraid, "uploaded_file", None):
		with open(vmraid.uploaded_file, "r") as upfile:
			fcontent = upfile.read()
	else:
		_file = vmraid.new_doc("File")
		fcontent = _file.get_uploaded_content()
	return read_csv_content(fcontent, ignore_encoding)

def read_csv_content_from_attached_file(doc):
	fileid = vmraid.get_all("File", fields = ["name"], filters = {"attached_to_doctype": doc.doctype,
		"attached_to_name":doc.name}, order_by="creation desc")

	if fileid : fileid = fileid[0].name

	if not fileid:
		msgprint(_("File not attached"))
		raise Exception

	try:
		_file = vmraid.get_doc("File", fileid)
		fcontent = _file.get_content()
		return read_csv_content(fcontent, vmraid.form_dict.get('ignore_encoding_errors'))
	except Exception:
		vmraid.throw(_("Unable to open attached file. Did you export it as CSV?"), title=_('Invalid CSV Format'))

def read_csv_content(fcontent, ignore_encoding=False):
	rows = []

	if not isinstance(fcontent, text_type):
		decoded = False
		for encoding in ["utf-8", "windows-1250", "windows-1252"]:
			try:
				fcontent = text_type(fcontent, encoding)
				decoded = True
				break
			except UnicodeDecodeError:
				continue

		if not decoded:
			vmraid.msgprint(_("Unknown file encoding. Tried utf-8, windows-1250, windows-1252."), raise_exception=True)

	fcontent = fcontent.encode("utf-8")
	content  = [ ]
	for line in fcontent.splitlines(True):
		if six.PY2:
			content.append(line)
		else:
			content.append(vmraid.safe_decode(line))

	try:
		rows = []
		for row in csv.reader(content):
			r = []
			for val in row:
				# decode everything
				val = val.strip()

				if val=="":
					# reason: in maraidb strict config, one cannot have blank strings for non string datatypes
					r.append(None)
				else:
					r.append(val)

			rows.append(r)

		return rows

	except Exception:
		vmraid.msgprint(_("Not a valid Comma Separated Value (CSV File)"))
		raise

@vmraid.whitelist()
def send_csv_to_client(args):
	if isinstance(args, string_types):
		args = json.loads(args)

	args = vmraid._dict(args)

	vmraid.response["result"] = cstr(to_csv(args.data))
	vmraid.response["doctype"] = args.filename
	vmraid.response["type"] = "csv"

def to_csv(data):
	writer = UnicodeWriter()
	for row in data:
		writer.writerow(row)

	return writer.getvalue()

def build_csv_response(data, filename):
	vmraid.response["result"] = cstr(to_csv(data))
	vmraid.response["doctype"] = filename
	vmraid.response["type"] = "csv"

class UnicodeWriter:
	def __init__(self, encoding="utf-8", quoting=csv.QUOTE_NONNUMERIC):
		self.encoding = encoding
		self.queue = StringIO()
		self.writer = csv.writer(self.queue, quoting=quoting)

	def writerow(self, row):
		if six.PY2:
			row = encode(row, self.encoding)
		self.writer.writerow(row)

	def getvalue(self):
		return self.queue.getvalue()

def check_record(d):
	"""check for mandatory, select options, dates. these should ideally be in doclist"""
	from vmraid.utils.dateutils import parse_date
	doc = vmraid.get_doc(d)

	for key in d:
		docfield = doc.meta.get_field(key)
		val = d[key]
		if docfield:
			if docfield.reqd and (val=='' or val==None):
				vmraid.msgprint(_("{0} is required").format(docfield.label), raise_exception=1)

			if docfield.fieldtype=='Select' and val and docfield.options:
				if val not in docfield.options.split('\n'):
					vmraid.throw(_("{0} must be one of {1}").format(_(docfield.label), comma_or(docfield.options.split("\n"))))

			if val and docfield.fieldtype=='Date':
				d[key] = parse_date(val)
			elif val and docfield.fieldtype in ["Int", "Check"]:
				d[key] = cint(val)
			elif val and docfield.fieldtype in ["Currency", "Float", "Percent"]:
				d[key] = flt(val)

def import_doc(d, doctype, overwrite, row_idx, submit=False, ignore_links=False):
	"""import main (non child) document"""
	if d.get("name") and vmraid.db.exists(doctype, d['name']):
		if overwrite:
			doc = vmraid.get_doc(doctype, d['name'])
			doc.flags.ignore_links = ignore_links
			doc.update(d)
			if d.get("docstatus") == 1:
				doc.update_after_submit()
			elif d.get("docstatus") == 0 and submit:
				doc.submit()
			else:
				doc.save()
			return 'Updated row (#%d) %s' % (row_idx + 1, getlink(doctype, d['name']))
		else:
			return 'Ignored row (#%d) %s (exists)' % (row_idx + 1,
				getlink(doctype, d['name']))
	else:
		doc = vmraid.get_doc(d)
		doc.flags.ignore_links = ignore_links
		doc.insert()

		if submit:
			doc.submit()

		return 'Inserted row (#%d) %s' % (row_idx + 1, getlink(doctype,
			doc.get('name')))

def getlink(doctype, name):
	return '<a href="/app/Form/%(doctype)s/%(name)s">%(name)s</a>' % locals()

def get_csv_content_from_google_sheets(url):
	# https://docs.google.com/spreadsheets/d/{sheetid}}/edit#gid={gid}
	validate_google_sheets_url(url)
	# get gid, defaults to first sheet
	if "gid=" in url:
		gid = url.rsplit('gid=', 1)[1]
	else:
		gid = 0
	# remove /edit path
	url = url.rsplit('/edit', 1)[0]
	# add /export path,
	url = url + '/export?format=csv&gid={0}'.format(gid)

	headers = {
		'Accept': 'text/csv'
	}
	response = requests.get(url, headers=headers)

	if response.ok:
		# if it returns html, it couldn't find the CSV content
		# because of invalid url or no access
		if response.text.strip().endswith('</html>'):
			vmraid.throw(
				_('Google Sheets URL is invalid or not publicly accessible.'),
				title=_("Invalid URL")
			)
		return response.content
	elif response.status_code == 400:
		vmraid.throw(_('Google Sheets URL must end with "gid={number}". Copy and paste the URL from the browser address bar and try again.'),
			title=_("Incorrect URL"))
	else:
		response.raise_for_status()

def validate_google_sheets_url(url):
	if "docs.google.com/spreadsheets" not in url:
		vmraid.throw(
			_('"{0}" is not a valid Google Sheets URL').format(url),
			title=_("Invalid URL"),
		)
