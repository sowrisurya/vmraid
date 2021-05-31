vmraid.provide('vmraid.model');
vmraid.provide('vmraid.utils');

/**
 * Opens the Website Meta Tag form if it exists for {route}
 * or creates a new doc and opens the form
 */
vmraid.utils.set_meta_tag = function(route) {
	vmraid.db.exists('Website Route Meta', route)
		.then(exists => {
			if (exists) {
				vmraid.set_route('Form', 'Website Route Meta', route);
			} else {
				// new doc
				const doc = vmraid.model.get_new_doc('Website Route Meta');
				doc.__newname = route;
				vmraid.set_route('Form', doc.doctype, doc.name);
			}
		});
};
