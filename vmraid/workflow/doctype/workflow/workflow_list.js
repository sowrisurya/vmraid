vmraid.listview_settings['Workflow'] = {
	add_fields: ["is_active"],
	get_indicator: function(doc) {
		if(doc.is_active) {
			return [__("Active"), "green", "is_active,=,Yes"];
		} else if(!doc.is_active) {
			return [__("Not active"), "gray", "is_active,=,No"];
		}
	}
};

vmraid.help.youtube_id["Workflow"] = "yObJUg9FxFs";
