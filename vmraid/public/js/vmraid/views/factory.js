// Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vmraid.provide('vmraid.pages');
vmraid.provide('vmraid.views');

vmraid.views.Factory = class Factory {
	constructor(opts) {
		$.extend(this, opts);
	}

	show() {
		var page_name = vmraid.get_route_str(),
			me = this;

		if (vmraid.pages[page_name]) {
			vmraid.container.change_to(page_name);
			if(me.on_show) {
				me.on_show();
			}
		} else {
			var route = vmraid.get_route();
			if(route[1]) {
				me.make(route);
			} else {
				vmraid.show_not_found(route);
			}
		}
	}

	make_page(double_column, page_name) {
		return vmraid.make_page(double_column, page_name);
	}
}

vmraid.make_page = function(double_column, page_name) {
	if(!page_name) {
		var page_name = vmraid.get_route_str();
	}
	var page = vmraid.container.add_page(page_name);

	vmraid.ui.make_app_page({
		parent: page,
		single_column: !double_column
	});
	vmraid.container.change_to(page_name);
	return page;
}
