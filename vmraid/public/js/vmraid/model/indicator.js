// Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors

vmraid.has_indicator = function(doctype) {
	// returns true if indicator is present
	if(vmraid.model.is_submittable(doctype)) {
		return true;
	} else if((vmraid.listview_settings[doctype] || {}).get_indicator
		|| vmraid.workflow.get_state_fieldname(doctype)) {
		return true;
	} else if(vmraid.meta.has_field(doctype, 'enabled')
		|| vmraid.meta.has_field(doctype, 'disabled')) {
		return true;
	}
	return false;
}

vmraid.get_indicator = function(doc, doctype) {
	if(doc.__unsaved) {
		return [__("Not Saved"), "orange"];
	}

	if(!doctype) doctype = doc.doctype;

	var workflow = vmraid.workflow.workflows[doctype];
	var without_workflow = workflow ? workflow['override_status'] : true;

	var settings = vmraid.listview_settings[doctype] || {};

	var is_submittable = vmraid.model.is_submittable(doctype),
		workflow_fieldname = vmraid.workflow.get_state_fieldname(doctype);

	// workflow
	if(workflow_fieldname && !without_workflow) {
		var value = doc[workflow_fieldname];
		if(value) {
			var colour = "";

			if(locals["Workflow State"][value] && locals["Workflow State"][value].style) {
				var colour = {
					"Success": "green",
					"Warning": "orange",
					"Danger": "red",
					"Primary": "blue",
					"Inverse": "black",
					"Info": "light-blue",
				}[locals["Workflow State"][value].style];
			}
			if (!colour) colour = "gray";

			return [__(value), colour, workflow_fieldname + ',=,' + value];
		}
	}

	// draft if document is submittable
	if(is_submittable && doc.docstatus==0 && !settings.has_indicator_for_draft) {
		return [__("Draft"), "red", "docstatus,=,0"];
	}

	// cancelled
	if(is_submittable && doc.docstatus==2 && !settings.has_indicator_for_cancelled) {
		return [__("Cancelled"), "red", "docstatus,=,2"];
	}

	if(settings.get_indicator) {
		var indicator = settings.get_indicator(doc);
		if(indicator) return indicator;
	}

	// if submittable
	if(is_submittable && doc.docstatus==1) {
		return [__("Submitted"), "blue", "docstatus,=,1"];
	}

	// based on status
	if(doc.status) {
		return [__(doc.status), vmraid.utils.guess_colour(doc.status)];
	}

	// based on enabled
	if(vmraid.meta.has_field(doctype, 'enabled')) {
		if(doc.enabled) {
			return [__('Enabled'), 'blue', 'enabled,=,1'];
		} else {
			return [__('Disabled'), 'grey', 'enabled,=,0'];
		}
	}

	// based on disabled
	if(vmraid.meta.has_field(doctype, 'disabled')) {
		if(doc.disabled) {
			return [__('Disabled'), 'grey', 'disabled,=,1'];
		} else {
			return [__('Enabled'), 'blue', 'disabled,=,0'];
		}
	}
}
