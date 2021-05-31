// Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vmraid.provide("vmraid.workflow");

vmraid.workflow = {
	state_fields: {},
	workflows: {},
	setup: function(doctype) {
		var wf = vmraid.get_list("Workflow", {document_type: doctype});
		if(wf.length) {
			vmraid.workflow.workflows[doctype] = wf[0];
			vmraid.workflow.state_fields[doctype] = wf[0].workflow_state_field;
		} else {
			vmraid.workflow.state_fields[doctype] = null;
		}
	},
	get_state_fieldname: function(doctype) {
		if(vmraid.workflow.state_fields[doctype]===undefined) {
			vmraid.workflow.setup(doctype);
		}
		return vmraid.workflow.state_fields[doctype];
	},
	get_default_state: function(doctype, docstatus) {
		vmraid.workflow.setup(doctype);
		var value = null;
		$.each(vmraid.workflow.workflows[doctype].states, function(i, workflow_state) {
			if(cint(workflow_state.doc_status)===cint(docstatus)) {
				value = workflow_state.state;
				return false;
			}
		});
		return value;
	},
	get_transitions: function(doc) {
		vmraid.workflow.setup(doc.doctype);
		return vmraid.xcall('vmraid.model.workflow.get_transitions', {doc: doc});
	},
	get_document_state: function(doctype, state) {
		vmraid.workflow.setup(doctype);
		return vmraid.get_children(vmraid.workflow.workflows[doctype], "states", {state:state})[0];
	},
	is_self_approval_enabled: function(doctype) {
		return vmraid.workflow.workflows[doctype].allow_self_approval;
	},
	is_read_only: function(doctype, name) {
		var state_fieldname = vmraid.workflow.get_state_fieldname(doctype);
		if(state_fieldname) {
			var doc = locals[doctype][name];
			if(!doc)
				return false;
			if(doc.__islocal)
				return false;

			var state = doc[state_fieldname] ||
				vmraid.workflow.get_default_state(doctype, doc.docstatus);

			var allow_edit = state ? vmraid.workflow.get_document_state(doctype, state) && vmraid.workflow.get_document_state(doctype, state).allow_edit : null;

			if(!vmraid.user_roles.includes(allow_edit)) {
				return true;
			}
		}
		return false;
	},
	get_update_fields: function(doctype) {
		var update_fields = $.unique($.map(vmraid.workflow.workflows[doctype].states || [],
			function(d) {
				return d.update_field;
			}));
		return update_fields;
	},
	get_state(doc) {
		const state_field = this.get_state_fieldname(doc.doctype);
		let state = doc[state_field];
		if (!state) {
			state = this.get_default_state(doc.doctype, doc.docstatus);
		}
		return state;
	},
	get_all_transitions(doctype) {
		return vmraid.workflow.workflows[doctype].transitions || [];
	},
	get_all_transition_actions(doctype) {
		const transitions = this.get_all_transitions(doctype);
		return transitions.map(transition => {
			return transition.action;
		});
	},
};
