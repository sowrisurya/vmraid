vmraid.listview_settings['Event'] = {
	add_fields: ["starts_on", "ends_on"],
	onload: function() {
		vmraid.route_options = {
			"status": "Open"
		};
	}
}