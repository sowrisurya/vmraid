/* eslint semi: "never" */
vmraid.ui.form.on('Chat Profile', {
	refresh: function (form) {
		if ( form.doc.name !== vmraid.session.user ) {
			form.disable_save()
			form.set_read_only(true)
			// There's one more that faris@vmraid.io told me to add here. form.refresh_fields()?
		}
	}
});
