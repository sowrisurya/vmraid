vmraid.route_history_queue = [];
const routes_to_skip = ['Form', 'social', 'setup-wizard', 'recorder'];

const save_routes = vmraid.utils.debounce(() => {
	if (vmraid.session.user === 'Guest') return;
	const routes = vmraid.route_history_queue;
	vmraid.route_history_queue = [];
	
	vmraid.xcall('vmraid.deferred_insert.deferred_insert', {
		'doctype': 'Route History',
		'records': routes
	}).catch(() => {
		vmraid.route_history_queue.concat(routes);
	});	

}, 10000);

vmraid.router.on('change', () => {
	const route = vmraid.get_route();
	if (is_route_useful(route)) {
		vmraid.route_history_queue.push({
			'user': vmraid.session.user,
			'creation': vmraid.datetime.now_datetime(),
			'route': vmraid.get_route_str()
		});

		save_routes();
	}
});

function is_route_useful(route) {
	if (!route[1]) {
		return false;
	} else if ((route[0] === 'List' && !route[2]) || routes_to_skip.includes(route[0])) {
		return false;
	} else {
		return true;
	}
}