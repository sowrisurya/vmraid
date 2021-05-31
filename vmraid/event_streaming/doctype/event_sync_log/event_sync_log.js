// Copyright (c) 2019, VMRaid Technologies and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Event Sync Log', {
	refresh: function(frm) {
		if (frm.doc.status == 'Failed') {
			frm.add_custom_button(__('Resync'), function() {
				vmraid.call({
					method: "vmraid.event_streaming.doctype.event_producer.event_producer.resync",
					args: {
						update: frm.doc,
					},
					callback: function(r) {
						if (r.message) {
							vmraid.msgprint(r.message);
							frm.set_value('status', r.message);
							frm.save();
						}
					}
				});
			});
		}
	}
});
