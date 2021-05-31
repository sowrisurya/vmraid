vmraid.listview_settings['Chat Room'] = {
	filters: [
		['Chat Room', 'owner', '=', vmraid.session.user, true],
		['Chat Room User', 'user', '=', vmraid.session.user, true]
	]
};