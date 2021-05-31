vmraid.pages['user-profile'].on_page_load = function (wrapper) {
	vmraid.require('user_profile_controller.bundle.js', () => {
		let user_profile = new vmraid.ui.UserProfile(wrapper);
		user_profile.show();
	});
};
