vmraid.provide('vmraid.ui.misc');
vmraid.ui.misc.about = function() {
	if(!vmraid.ui.misc.about_dialog) {
		var d = new vmraid.ui.Dialog({title: __('VMRaid Framework')});

		$(d.body).html(repl("<div>\
		<p>"+__("Open Source Applications for the Web")+"</p>  \
		<p><i class='fa fa-globe fa-fw'></i>\
			Website: <a href='https://vmraidframework.com' target='_blank'>https://vmraidframework.com</a></p>\
		<p><i class='fa fa-github fa-fw'></i>\
			Source: <a href='https://github.com/vmraid' target='_blank'>https://github.com/vmraid</a></p>\
		<p><i class='fa fa-linkedin fa-fw'></i>\
			Linkedin: <a href='https://linkedin.com/company/vmraid-tech' target='_blank'>https://linkedin.com/company/vmraid-tech</a></p>\
		<p><i class='fa fa-facebook fa-fw'></i>\
			Facebook: <a href='https://facebook.com/erpadda' target='_blank'>https://facebook.com/erpadda</a></p>\
		<p><i class='fa fa-twitter fa-fw'></i>\
			Twitter: <a href='https://twitter.com/erpadda' target='_blank'>https://twitter.com/erpadda</a></p>\
		<hr>\
		<h4>Installed Apps</h4>\
		<div id='about-app-versions'>Loading versions...</div>\
		<hr>\
		<p class='text-muted'>&copy; VMRaid Technologies Pvt. Ltd and contributors </p> \
		</div>", vmraid.app));

		vmraid.ui.misc.about_dialog = d;

		vmraid.ui.misc.about_dialog.on_page_show = function() {
			if(!vmraid.versions) {
				vmraid.call({
					method: "vmraid.utils.change_log.get_versions",
					callback: function(r) {
						show_versions(r.message);
					}
				})
			} else {
				show_versions(vmraid.versions);
			}
		};

		var show_versions = function(versions) {
			var $wrap = $("#about-app-versions").empty();
			$.each(Object.keys(versions).sort(), function(i, key) {
				var v = versions[key];
				if(v.branch) {
					var text = $.format('<p><b>{0}:</b> v{1} ({2})<br></p>',
						[v.title, v.branch_version || v.version, v.branch])
				} else {
					var text = $.format('<p><b>{0}:</b> v{1}<br></p>',
						[v.title, v.version])
				}
				$(text).appendTo($wrap);
			});

			vmraid.versions = versions;
		}

	}

	vmraid.ui.misc.about_dialog.show();

}
