from __future__ import unicode_literals

import vmraid

def execute():
	communications = vmraid.db.sql("""
		SELECT
			`tabCommunication`.name, `tabCommunication`.creation, `tabCommunication`.modified,
			`tabCommunication`.modified_by,`tabCommunication`.timeline_doctype, `tabCommunication`.timeline_name,
			`tabCommunication`.link_doctype, `tabCommunication`.link_name
		FROM `tabCommunication`
		WHERE `tabCommunication`.communication_medium='Email'
	""", as_dict=True)

	name = 1000000000
	values = []

	for count, communication in enumerate(communications):
		counter = 1
		if communication.timeline_doctype and communication.timeline_name:
			name += 1
			values.append("""({0}, "{1}", "timeline_links", "Communication", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}")""".format(
				counter, str(name), vmraid.db.escape(communication.name), vmraid.db.escape(communication.timeline_doctype),
				vmraid.db.escape(communication.timeline_name), communication.creation, communication.modified, communication.modified_by
			))
			counter += 1
		if communication.link_doctype and communication.link_name:
			name += 1
			values.append("""({0}, "{1}", "timeline_links", "Communication", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}")""".format(
				counter, str(name), vmraid.db.escape(communication.name), vmraid.db.escape(communication.link_doctype),
				vmraid.db.escape(communication.link_name), communication.creation, communication.modified, communication.modified_by
			))

		if values and (count % 10000 == 0 or count == len(communications) - 1):
			vmraid.db.sql("""
				INSERT INTO `tabCommunication Link`
					(`idx`, `name`, `parentfield`, `parenttype`, `parent`, `link_doctype`, `link_name`, `creation`,
					`modified`, `modified_by`)
				VALUES {0}
			""".format(", ".join([d for d in values])))

			values = []

	vmraid.db.add_index("Communication Link", ["link_doctype", "link_name"])
