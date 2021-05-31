vmraid.ui.form.ControlText = class ControlText extends vmraid.ui.form.ControlData {
	static html_element = "textarea"
	static horizontal = false
	make_wrapper() {
		super.make_wrapper();
		this.$wrapper.find(".like-disabled-input").addClass("for-description");
	}
	make_input() {
		super.make_input();
		this.$input.css({'height': '300px'});
	}
};

vmraid.ui.form.ControlLongText = vmraid.ui.form.ControlText;
vmraid.ui.form.ControlSmallText = class ControlSmallText extends vmraid.ui.form.ControlText {
	make_input() {
		super.make_input();
		this.$input.css({'height': '150px'});
	}
};
