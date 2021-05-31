vmraid.listview_settings['Chat Message'] = {
	filters: [
		['Chat Message', 'user',  '==', vmraid.session.user, true]
		// I need an or_filter here.
		// ['Chat Room',    'owner', '==', vmraid.session.user, true],
		// ['Chat Room',    vmraid.session.user, 'in', 'users', true]
	]
};