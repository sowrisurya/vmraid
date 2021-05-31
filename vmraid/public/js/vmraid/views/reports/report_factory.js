// Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vmraid.views.ReportFactory = class ReportFactory extends vmraid.views.Factory {
	make(route) {
		const _route = ['List', route[1], 'Report'];

		if (route[2]) {
			// custom report
			_route.push(route[2]);
		}

		vmraid.set_route(_route);
	}
}
