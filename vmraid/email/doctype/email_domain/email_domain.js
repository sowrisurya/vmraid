
vmraid.ui.form.on("Email Domain", {
	email_id:function(frm){
		frm.set_value("domain_name",frm.doc.email_id.split("@")[1])
	},

	refresh:function(frm){
		if (frm.doc.email_id){
			frm.set_value("domain_name",frm.doc.email_id.split("@")[1])
		}

		if (frm.doc.__islocal != 1 && vmraid.route_flags.return_to_email_account) {
			var route = vmraid.get_prev_route();
			delete vmraid.route_flags.return_to_email_account;
			vmraid.route_flags.set_domain_values = true

			vmraid.route_options = {
				domain: frm.doc.name,
				use_imap: frm.doc.use_imap,
				email_server: frm.doc.email_server,
				use_ssl: frm.doc.use_ssl,
				smtp_server: frm.doc.smtp_server,
				use_tls: frm.doc.use_tls,
				smtp_port: frm.doc.smtp_port
			},
			vmraid.set_route(route);
		}
	}
})