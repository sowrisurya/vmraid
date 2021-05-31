// Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

// provide a namespace
if(!window.vmraid)
	window.vmraid = {};

vmraid.provide = function(namespace) {
	// docs: create a namespace //
	var nsl = namespace.split('.');
	var parent = window;
	for(var i=0; i<nsl.length; i++) {
		var n = nsl[i];
		if(!parent[n]) {
			parent[n] = {}
		}
		parent = parent[n];
	}
	return parent;
}

vmraid.provide("locals");
vmraid.provide("vmraid.flags");
vmraid.provide("vmraid.settings");
vmraid.provide("vmraid.utils");
vmraid.provide("vmraid.ui.form");
vmraid.provide("vmraid.modules");
vmraid.provide("vmraid.templates");
vmraid.provide("vmraid.test_data");
vmraid.provide('vmraid.utils');
vmraid.provide('vmraid.model');
vmraid.provide('vmraid.user');
vmraid.provide('vmraid.session');
vmraid.provide('locals.DocType');

// for listviews
vmraid.provide("vmraid.listview_settings");
vmraid.provide("vmraid.tour");
vmraid.provide("vmraid.listview_parent_route");

// constants
window.NEWLINE = '\n';
window.TAB = 9;
window.UP_ARROW = 38;
window.DOWN_ARROW = 40;

// proxy for user globals defined in desk.js

// API globals
window.cur_frm=null;
