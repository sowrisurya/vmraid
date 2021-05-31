import vmraid

def update_system_settings(args):
	doc = vmraid.get_doc('System Settings')
	doc.update(args)
	doc.flags.ignore_mandatory = 1
	doc.save()

def get_system_setting(key):
	return vmraid.db.get_single_value("System Settings", key)

global_test_dependencies = ['User']
