// Copyright (c) 2019, VMRaid Technologies and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Notification Log', {
	refresh: function(frm) {
		if (frm.doc.attached_file) {
			frm.trigger('set_attachment');
		} else {
			frm.get_field('attachment_link').$wrapper.empty();
		}
	},

	open_reference_document: function(frm) {
		const dt = frm.doc.document_type;
		const dn = frm.doc.document_name;
		vmraid.set_route('Form', dt, dn);
	},

	set_attachment: function(frm) {
		const attachment = JSON.parse(frm.doc.attached_file);

		const $wrapper = frm.get_field('attachment_link').$wrapper;
		$wrapper.html(`
			<div class="attached-file text-medium">
				<div class="ellipsis">
					<i class="fa fa-paperclip"></i>
					<a class="attached-file-link">${attachment.name}.pdf</a>
				</div>
			</div>
		`);

		$wrapper.find(".attached-file-link").click(() => {
			const w = window.open(
				vmraid.urllib.get_full_url(`/api/method/vmraid.utils.print_format.download_pdf?
					doctype=${encodeURIComponent(attachment.doctype)}
					&name=${encodeURIComponent(attachment.name)}
					&format=${encodeURIComponent(attachment.print_format)}
					&lang=${encodeURIComponent(attachment.lang)}`)
			);
			if (!w) {
				vmraid.msgprint(__("Please enable pop-ups"));
			}
		});
	}
});
