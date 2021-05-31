// Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vmraid.db = {
	get_list: function(doctype, args) {
		if (!args) {
			args = {};
		}
		args.doctype = doctype;
		if (!args.fields) {
			args.fields = ['name'];
		}
		if (!args.limit) {
			args.limit = 20;
		}
		return new Promise ((resolve) => {
			vmraid.call({
				method: 'vmraid.desk.reportview.get_list',
				args: args,
				type: 'GET',
				callback: function(r) {
					resolve(r.message);
				}
			});
		});
	},
	exists: function(doctype, name) {
		return new Promise ((resolve) => {
			vmraid.db.get_value(doctype, {name: name}, 'name').then((r) => {
				(r.message && r.message.name) ? resolve(true) : resolve(false);
			});
		});
	},
	get_value: function(doctype, filters, fieldname, callback, parent_doc) {
		return vmraid.call({
			method: "vmraid.client.get_value",
			type: 'GET',
			args: {
				doctype: doctype,
				fieldname: fieldname,
				filters: filters,
				parent: parent_doc
			},
			callback: function(r) {
				callback && callback(r.message);
			}
		});
	},
	get_single_value: (doctype, field) => {
		return new Promise(resolve => {
			vmraid.call({
				method: 'vmraid.client.get_single_value',
				args: { doctype, field },
				type: 'GET',
			}).then(r => resolve(r ? r.message : null));
		});
	},
	set_value: function(doctype, docname, fieldname, value, callback) {
		return vmraid.call({
			method: "vmraid.client.set_value",
			args: {
				doctype: doctype,
				name: docname,
				fieldname: fieldname,
				value: value
			},
			callback: function(r) {
				callback && callback(r.message);
			}
		});
	},
	get_doc: function(doctype, name, filters = null) {
		return new Promise((resolve, reject) => {
			vmraid.call({
				method: "vmraid.client.get",
				type: 'GET',
				args: { doctype, name, filters },
				callback: r => {
					vmraid.model.sync(r.message);
					resolve(r.message);
				}
			}).fail(reject);
		});
	},
	insert: function(doc) {
		return vmraid.xcall('vmraid.client.insert', { doc });
	},
	delete_doc: function(doctype, name) {
		return new Promise(resolve => {
			vmraid.call('vmraid.client.delete', { doctype, name }, r => resolve(r.message));
		});
	},
	count: function(doctype, args={}) {
		let filters = args.filters || {};

		// has a filter with childtable?
		const distinct = Array.isArray(filters) && filters.some(filter => {
			return filter[0] !== doctype;
		});

		const fields = [];

		return vmraid.xcall('vmraid.desk.reportview.get_count', {
			doctype,
			filters,
			fields,
			distinct,
		});
	},
	get_link_options(doctype, txt = '', filters={}) {
		return new Promise(resolve => {
			vmraid.call({
				type: 'GET',
				method: 'vmraid.desk.search.search_link',
				args: {
					doctype,
					txt,
					filters
				},
				callback(r) {
					resolve(r.results);
				}
			});
		});
	}
};
