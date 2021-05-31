import vmraid

def execute():
	'''
		Remove GCalendar and GCalendar Settings
		Remove Google Maps Settings as its been merged with Delivery Trips
	'''
	vmraid.delete_doc_if_exists('DocType', 'GCalendar Account')
	vmraid.delete_doc_if_exists('DocType', 'GCalendar Settings')
	vmraid.delete_doc_if_exists('DocType', 'Google Maps Settings')
