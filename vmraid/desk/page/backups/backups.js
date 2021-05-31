vmraid.pages['backups'].on_page_load = function(wrapper) {
	var page = vmraid.ui.make_app_page({
		parent: wrapper,
		title: __('Download Backups'),
		single_column: true
	});

	page.add_inner_button(__("Set Number of Backups"), function () {
		vmraid.set_route('Form', 'System Settings');
	});

	page.add_inner_button(__("Download Files Backup"), function () {
		vmraid.call({
			method:"vmraid.desk.page.backups.backups.schedule_files_backup",
			args: {"user_email": vmraid.session.user_email}
		});
	});

	vmraid.breadcrumbs.add("Setup");

	$(vmraid.render_template("backups")).appendTo(page.body.addClass("no-border"));
}
