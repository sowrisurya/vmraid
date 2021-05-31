vmraid.user_info = function(uid) {
	if(!uid)
		uid = vmraid.session.user;

	if(uid.toLowerCase()==="bot") {
		return {
			fullname: __("Bot"),
			image: "/assets/vmraid/images/ui/bot.png",
			abbr: "B"
		};
	}

	if(!(vmraid.boot.user_info && vmraid.boot.user_info[uid])) {
		var user_info = {
			fullname: vmraid.utils.capitalize(uid.split("@")[0]) || "Unknown"
		};
	} else {
		var user_info = vmraid.boot.user_info[uid];
	}

	user_info.abbr = vmraid.get_abbr(user_info.fullname);
	user_info.color = vmraid.get_palette(user_info.fullname);

	return user_info;
};

vmraid.ui.set_user_background = function(src, selector, style) {
	if(!selector) selector = "#page-desktop";
	if(!style) style = "Fill Screen";
	if(src) {
		if (window.cordova && src.indexOf("http") === -1) {
			src = vmraid.base_url + src;
		}
		var background = repl('background: url("%(src)s") center center;', {src: src});
	} else {
		var background = "background-color: #4B4C9D;";
	}

	vmraid.dom.set_style(repl('%(selector)s { \
		%(background)s \
		background-attachment: fixed; \
		%(style)s \
	}', {
		selector:selector,
		background:background,
		style: style==="Fill Screen" ? "background-size: cover;" : ""
	}));
};

vmraid.provide('vmraid.user');

$.extend(vmraid.user, {
	name: 'Guest',
	full_name: function(uid) {
		return uid === vmraid.session.user ?
			__("You", null, "Name of the current user. For example: You edited this 5 hours ago.") :
			vmraid.user_info(uid).fullname;
	},
	image: function(uid) {
		return vmraid.user_info(uid).image;
	},
	abbr: function(uid) {
		return vmraid.user_info(uid).abbr;
	},
	has_role: function(rl) {
		if(typeof rl=='string')
			rl = [rl];
		for(var i in rl) {
			if((vmraid.boot ? vmraid.boot.user.roles : ['Guest']).indexOf(rl[i])!=-1)
				return true;
		}
	},
	get_desktop_items: function() {
		// hide based on permission
		var modules_list = $.map(vmraid.boot.allowed_modules, function(icon) {
			var m = icon.module_name;
			var type = vmraid.modules[m] && vmraid.modules[m].type;

			if(vmraid.boot.user.allow_modules.indexOf(m) === -1) return null;

			var ret = null;
			if (type === "module") {
				if(vmraid.boot.user.allow_modules.indexOf(m)!=-1 || vmraid.modules[m].is_help)
					ret = m;
			} else if (type === "page") {
				if(vmraid.boot.allowed_pages.indexOf(vmraid.modules[m].link)!=-1)
					ret = m;
			} else if (type === "list") {
				if(vmraid.model.can_read(vmraid.modules[m]._doctype))
					ret = m;
			} else if (type === "view") {
				ret = m;
			} else if (type === "setup") {
				if(vmraid.user.has_role("System Manager") || vmraid.user.has_role("Administrator"))
					ret = m;
			} else {
				ret = m;
			}

			return ret;
		});

		return modules_list;
	},

	is_report_manager: function() {
		return vmraid.user.has_role(['Administrator', 'System Manager', 'Report Manager']);
	},

	get_formatted_email: function(email) {
		var fullname = vmraid.user.full_name(email);

		if (!fullname) {
			return email;
		} else {
			// to quote or to not
			var quote = '';

			// only if these special characters are found
			// why? To make the output same as that in python!
			if (fullname.search(/[\[\]\\()<>@,:;".]/) !== -1) {
				quote = '"';
			}

			return repl('%(quote)s%(fullname)s%(quote)s <%(email)s>', {
				fullname: fullname,
				email: email,
				quote: quote
			});
		}
	},

	get_emails: ( ) => {
		return Object.keys(vmraid.boot.user_info).map(key => vmraid.boot.user_info[key].email);
	},

	/* Normally vmraid.user is an object
	 * having properties and methods.
	 * But in the following case
	 *
	 * if (vmraid.user === 'Administrator')
	 *
	 * vmraid.user will cast to a string
	 * returning vmraid.user.name
	 */
	toString: function() {
		return this.name;
	}
});

vmraid.session_alive = true;
$(document).bind('mousemove', function() {
	if(vmraid.session_alive===false) {
		$(document).trigger("session_alive");
	}
	vmraid.session_alive = true;
	if(vmraid.session_alive_timeout)
		clearTimeout(vmraid.session_alive_timeout);
	vmraid.session_alive_timeout = setTimeout('vmraid.session_alive=false;', 30000);
});