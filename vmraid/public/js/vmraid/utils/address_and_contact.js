vmraid.provide('vmraid.contacts')

$.extend(vmraid.contacts, {
	clear_address_and_contact: function(frm) {
		$(frm.fields_dict['address_html'].wrapper).html("");
		frm.fields_dict['contact_html'] && $(frm.fields_dict['contact_html'].wrapper).html("");
	},

	render_address_and_contact: function(frm) {
		// render address
		if(frm.fields_dict['address_html'] && "addr_list" in frm.doc.__onload) {
			$(frm.fields_dict['address_html'].wrapper)
				.html(vmraid.render_template("address_list",
					frm.doc.__onload))
				.find(".btn-address").on("click", function() {
					vmraid.new_doc("Address");
				});
		}

		// render contact
		if(frm.fields_dict['contact_html'] && "contact_list" in frm.doc.__onload) {
			$(frm.fields_dict['contact_html'].wrapper)
				.html(vmraid.render_template("contact_list",
					frm.doc.__onload))
				.find(".btn-contact").on("click", function() {
					vmraid.new_doc("Contact");
				}
			);
		}
	},
	get_last_doc: function(frm) {
		const reverse_routes = vmraid.route_history.reverse();
		const last_route = reverse_routes.find(route => {
			return route[0] === 'Form' && route[1] !== frm.doctype
		})
		let doctype = last_route && last_route[1];
		let docname = last_route && last_route[2];

		if (last_route && last_route.length > 3)
			docname = last_route.slice(2).join("/");

		return {
			doctype,
			docname
		}
	}
})