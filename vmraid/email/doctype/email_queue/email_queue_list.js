vmraid.listview_settings['Email Queue'] = {
	get_indicator: function(doc) {
		var colour = {'Sent': 'green', 'Sending': 'blue', 'Not Sent': 'grey', 'Error': 'red', 'Expired': 'orange'};
		return [__(doc.status), colour[doc.status], "status,=," + doc.status];
	},
	refresh: function(doclist){
		if (has_common(vmraid.user_roles, ["Administrator", "System Manager"])){
			if (cint(vmraid.defaults.get_default("hold_queue"))){
				doclist.page.clear_inner_toolbar()
				doclist.page.add_inner_button(__("Resume Sending"), function() {
					vmraid.defaults.set_default("hold_queue", 0);
					cur_list.refresh();
				})
			} else {
				doclist.page.clear_inner_toolbar()
				doclist.page.add_inner_button(__("Suspend Sending"), function() {
					vmraid.defaults.set_default("hold_queue", 1)
					cur_list.refresh();
				})
			}
		}
	}
}
