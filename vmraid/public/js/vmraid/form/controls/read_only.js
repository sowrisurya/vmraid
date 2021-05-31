vmraid.ui.form.ControlReadOnly = class ControlReadOnly extends vmraid.ui.form.ControlData {
	get_status(explain) {
		var status = super.get_status(explain);
		if(status==="Write")
			status = "Read";
		return;
	}
};
