from __future__ import unicode_literals
import vmraid

def execute():
	vmraid.reload_doctype('Event')
	# Rename "Cancel" to "Cancelled"
	vmraid.db.sql("""UPDATE tabEvent set event_type='Cancelled' where event_type='Cancel'""")
	# Move references to Participants table
	events = vmraid.db.sql("""SELECT name, ref_type, ref_name FROM tabEvent WHERE ref_type!=''""", as_dict=True)
	for event in events:
		if event.ref_type and event.ref_name:
			try:
				e = vmraid.get_doc('Event', event.name)
				e.append('event_participants', {"reference_doctype": event.ref_type, "reference_docname": event.ref_name})
				e.flags.ignore_mandatory   = True
				e.flags.ignore_permissions = True
				e.save()
			except Exception:
				vmraid.log_error(vmraid.get_traceback())