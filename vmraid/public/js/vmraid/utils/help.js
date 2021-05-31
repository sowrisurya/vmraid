// Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vmraid.provide("vmraid.help");

vmraid.help.youtube_id = {};

vmraid.help.has_help = function (doctype) {
	return vmraid.help.youtube_id[doctype];
}

vmraid.help.show = function (doctype) {
	if (vmraid.help.youtube_id[doctype]) {
		vmraid.help.show_video(vmraid.help.youtube_id[doctype]);
	}
}

vmraid.help.show_video = function (youtube_id, title) {
	if (vmraid.utils.is_url(youtube_id)) {
		const expression = '(?:youtube.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu.be/)([^"&?\\s]{11})';
		youtube_id = youtube_id.match(expression)[1];
	}

	// (vmraid.help_feedback_link || "")
	let dialog = new vmraid.ui.Dialog({
		title: title || __("Help"),
		size: 'large'
	});

	let video = $(`<div class="video-player" data-plyr-provider="youtube" data-plyr-embed-id="${youtube_id}"></div>`);
	video.appendTo(dialog.body);

	dialog.show();
	dialog.$wrapper.addClass("video-modal");

	let plyr = new vmraid.Plyr(video[0], {
		hideControls: true,
		resetOnEnd: true,
	});

	dialog.onhide = () => {
		plyr.destroy();
	};
}

$("body").on("click", "a.help-link", function () {
	var doctype = $(this).attr("data-doctype");
	doctype && vmraid.help.show(doctype);
});
