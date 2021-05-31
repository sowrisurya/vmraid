// Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vmraid.provide('vmraid.views.list_view');

window.cur_list = null;
vmraid.views.ListFactory = class ListFactory extends vmraid.views.Factory {
	make (route) {
		var me = this;
		var doctype = route[1];

		vmraid.model.with_doctype(doctype, function () {
			if (locals['DocType'][doctype].issingle) {
				vmraid.set_re_route('Form', doctype);
			} else {
				// List / Gantt / Kanban / etc
				// File is a special view
				const view_name = doctype !== 'File' ? vmraid.utils.to_title_case(route[2] || 'List') : 'File';
				let view_class = vmraid.views[view_name + 'View'];
				if (!view_class) view_class = vmraid.views.ListView;

				if (view_class && view_class.load_last_view && view_class.load_last_view()) {
					// view can have custom routing logic
					return;
				}

				vmraid.provide('vmraid.views.list_view.' + doctype);
				const page_name = vmraid.get_route_str();

				if (!vmraid.views.list_view[page_name]) {
					vmraid.views.list_view[page_name] = new view_class({
						doctype: doctype,
						parent: me.make_page(true, page_name)
					});
				} else {
					vmraid.container.change_to(page_name);
				}
				me.set_cur_list();
			}
		});
	}

	show() {
		if (this.re_route_to_view()) {
			return;
		}
		this.set_module_breadcrumb();
		super.show();
		this.set_cur_list();
		cur_list && cur_list.show();
	}

	re_route_to_view() {
		var route = vmraid.get_route();
		var doctype = route[1];
		var last_route = vmraid.route_history.slice(-2)[0];
		if (route[0] === 'List' && route.length === 2 && vmraid.views.list_view[doctype]) {
			if(last_route && last_route[0]==='List' && last_route[1]===doctype) {
				// last route same as this route, so going back.
				// this happens because /app/List/Item will redirect to /app/List/Item/List
				// while coming from back button, the last 2 routes will be same, so
				// we know user is coming in the reverse direction (via back button)

				// example:
				// Step 1: /app/List/Item redirects to /app/List/Item/List
				// Step 2: User hits "back" comes back to /app/List/Item
				// Step 3: Now we cannot send the user back to /app/List/Item/List so go back one more step
				window.history.go(-1);
				return true;
			} else {
				return false;
			}
		}
	}

	set_module_breadcrumb() {
		if (vmraid.route_history.length > 1) {
			var prev_route = vmraid.route_history[vmraid.route_history.length - 2];
			if (prev_route[0] === 'modules') {
				var doctype = vmraid.get_route()[1],
					module = prev_route[1];
				if (vmraid.module_links[module] && vmraid.module_links[module].includes(doctype)) {
					// save the last page from the breadcrumb was accessed
					vmraid.breadcrumbs.set_doctype_module(doctype, module);
				}
			}
		}
	}

	set_cur_list() {
		var route = vmraid.get_route();
		var page_name = vmraid.get_route_str();
		cur_list = vmraid.views.list_view[page_name];
		if (cur_list && cur_list.doctype !== route[1]) {
			// changing...
			window.cur_list = null;
		}
	}
}
