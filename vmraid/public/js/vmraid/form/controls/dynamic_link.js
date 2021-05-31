vmraid.ui.form.ControlDynamicLink = class ControlDynamicLink extends vmraid.ui.form.ControlLink {
	get_options() {
		let options = '';
		if (this.df.get_options) {
			options = this.df.get_options();
		} else if (this.docname==null && cur_dialog) {
			//for dialog box
			options = cur_dialog.get_value(this.df.options);
		} else if (!cur_frm) {
			const selector = `input[data-fieldname="${this.df.options}"]`;
			let input = null;
			if (cur_list) {
				// for list page
				input = cur_list.filter_area.standard_filters_wrapper.find(selector);
			}
			if (cur_page) {
				input = $(cur_page.page).find(selector);
			}
			if (input) {
				options = input.val();
			}
		} else {
			options = vmraid.model.get_value(this.df.parent, this.docname, this.df.options);
		}

		if (vmraid.model.is_single(options)) {
			vmraid.throw(__("{0} is not a valid DocType for Dynamic Link", [options.bold()]));
		}

		return options;
	}
};
