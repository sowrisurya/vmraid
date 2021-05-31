// Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

// for translation
vmraid._messages = {};
vmraid._ = function(txt, replace, context = null) {
	if ($.isEmptyObject(vmraid._messages) && vmraid.boot) {
		$.extend(vmraid._messages, vmraid.boot.__messages);
	}
	if (!txt) return txt;
	if (typeof txt != "string") return txt;

	let translated_text = '';

	let key = txt;    // txt.replace(/\n/g, "");
	if (context) {
		translated_text = vmraid._messages[`${key}:${context}`];
	}

	if (!translated_text) {
		translated_text = vmraid._messages[key] || txt;
	}

	if (replace && typeof replace === "object") {
		translated_text = $.format(translated_text, replace);
	}
	return translated_text;
};

window.__ = vmraid._;

vmraid.get_languages = function() {
	if (!vmraid.languages) {
		vmraid.languages = [];
		$.each(vmraid.boot.lang_dict, function(lang, value) {
			vmraid.languages.push({ label: lang, value: value });
		});
		vmraid.languages = vmraid.languages.sort(function(a, b) {
			return a.value < b.value ? -1 : 1;
		});
	}
	return vmraid.languages;
};
