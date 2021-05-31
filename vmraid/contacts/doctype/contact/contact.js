// Copyright (c) 2016, VMRaid Technologies and contributors
// For license information, please see license.txt

vmraid.ui.form.on("Contact", {
	onload(frm) {
		frm.email_field = "email_id";
	},
	refresh: function(frm) {
		if(frm.doc.__islocal) {
			const last_doc = vmraid.contacts.get_last_doc(frm);
			if(vmraid.dynamic_link && vmraid.dynamic_link.doc
					&& vmraid.dynamic_link.doc.name == last_doc.docname) {
				frm.set_value('links', '');
				frm.add_child('links', {
					link_doctype: vmraid.dynamic_link.doctype,
					link_name: vmraid.dynamic_link.doc[vmraid.dynamic_link.fieldname]
				});
			}
		}

		if(!frm.doc.user && !frm.is_new() && frm.perm[0].write) {
			frm.add_custom_button(__("Invite as User"), function() {
				return vmraid.call({
					method: "vmraid.contacts.doctype.contact.contact.invite_user",
					args: {
						contact: frm.doc.name
					},
					callback: function(r) {
						frm.set_value("user", r.message);
					}
				});
			});
		}
		frm.set_query('link_doctype', "links", function() {
			return {
				query: "vmraid.contacts.address_and_contact.filter_dynamic_link_doctypes",
				filters: {
					fieldtype: "HTML",
					fieldname: "contact_html",
				}
			}
		});
		frm.refresh_field("links");

		let numbers = frm.doc.phone_nos;
		if (numbers && numbers.length && vmraid.phone_call.handler) {
			frm.add_custom_button(__('Call'), () => {
				numbers = frm.doc.phone_nos
					.sort((prev, next) => next.is_primary_mobile_no - prev.is_primary_mobile_no)
					.map(d => d.phone);
				vmraid.phone_call.handler(numbers);
			});
		}

		if (frm.doc.links) {
			vmraid.call({
				method: "vmraid.contacts.doctype.contact.contact.address_query",
				args: {links: frm.doc.links},
				callback: function(r) {
					if (r && r.message) {
						frm.set_query("address", function () {
							return {
								filters: {
									name: ["in", r.message],
								}
							}
						});
					}
				}
			});

			for (let i in frm.doc.links) {
				let link = frm.doc.links[i];
				frm.add_custom_button(__("{0}: {1}", [__(link.link_doctype), __(link.link_name)]), function() {
					vmraid.set_route("Form", link.link_doctype, link.link_name);
				}, __("Links"));
			}
		}
	},
	validate: function(frm) {
		// clear linked customer / supplier / sales partner on saving...
		if(frm.doc.links) {
			frm.doc.links.forEach(function(d) {
				vmraid.model.remove_from_locals(d.link_doctype, d.link_name);
			});
		}
	},
	after_save: function(frm) {
		vmraid.run_serially([
			() => vmraid.timeout(1),
			() => {
				const last_doc = vmraid.contacts.get_last_doc(frm);
				if (vmraid.dynamic_link && vmraid.dynamic_link.doc && vmraid.dynamic_link.doc.name == last_doc.docname) {
					for (let i in frm.doc.links) {
						let link = frm.doc.links[i];
						if (last_doc.doctype == link.link_doctype && last_doc.docname == link.link_name) {
							vmraid.set_route('Form', last_doc.doctype, last_doc.docname);
						}
					}
				}
			}
		]);
	},
	sync_with_google_contacts: function(frm) {
		if (frm.doc.sync_with_google_contacts) {
			vmraid.db.get_value("Google Contacts", {"email_id": vmraid.session.user}, "name", (r) => {
				if (r && r.name) {
					frm.set_value("google_contacts", r.name);
				}
			})
		}
	}
});

vmraid.ui.form.on("Dynamic Link", {
	link_name:function(frm, cdt, cdn){
		var child = locals[cdt][cdn];
		if(child.link_name) {
			vmraid.model.with_doctype(child.link_doctype, function () {
				var title_field = vmraid.get_meta(child.link_doctype).title_field || "name"
				vmraid.model.get_value(child.link_doctype, child.link_name, title_field, function (r) {
					vmraid.model.set_value(cdt, cdn, "link_title", r[title_field])
				})
			})
		}
	}
})
