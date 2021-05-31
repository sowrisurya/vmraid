// Copyright (c) 2016, VMRaid Technologies and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Client Script', {
	refresh(frm) {
		if (frm.doc.dt && frm.doc.script) {
			frm.add_custom_button(__('Go to {0}', [frm.doc.dt]),
				() => vmraid.set_route('List', frm.doc.dt, 'List'));
		}

		if (frm.doc.view == 'Form') {
			frm.add_custom_button(__('Add script for Child Table'), () => {
				vmraid.model.with_doctype(frm.doc.dt, () => {
					const child_tables = vmraid.meta.get_docfields(frm.doc.dt, null, {
						fieldtype: 'Table'
					}).map(df => df.options);

					const d = new vmraid.ui.Dialog({
						title: __('Select Child Table'),
						fields: [
							{
								label: __('Select Child Table'),
								fieldtype: 'Link',
								fieldname: 'cdt',
								options: 'DocType',
								get_query: () => {
									return {
										filters: {
											istable: 1,
											name: ['in', child_tables]
										}
									};
								}
							}
						],
						primary_action: ({ cdt }) => {
							cdt = d.get_field('cdt').value;
							frm.events.add_script_for_doctype(frm, cdt);
							d.hide();
						}
					});

					d.show();
				});
			});
		}

		frm.set_query('dt', {
			filters: {
				istable: 0
			}
		});
	},

	dt(frm) {
		frm.toggle_display('view', !vmraid.boot.single_types.includes(frm.doc.dt));

		if (!frm.doc.script) {
			frm.events.add_script_for_doctype(frm, frm.doc.dt);
		}

		if (frm.doc.script && !frm.doc.script.includes(frm.doc.dt)) {
			frm.doc.script = '';
			frm.events.add_script_for_doctype(frm, frm.doc.dt);
		}
	},

	view(frm) {
		let has_form_boilerplate = frm.doc.script.includes('vmraid.ui.form.on')
		if (frm.doc.view === 'List' && has_form_boilerplate) {
			frm.set_value('script', '');
		}
		if (frm.doc.view === 'Form' && !has_form_boilerplate) {
			frm.trigger('dt');
		}
	},

	add_script_for_doctype(frm, doctype) {
		if (!doctype) return;
		let boilerplate = `
vmraid.ui.form.on('${doctype}', {
	refresh(frm) {
		// your code here
	}
})
		`.trim();
		let script = (frm.doc.script || '');
		if (script) {
			script += '\n\n';
		}
		frm.set_value('script', script + boilerplate);
	}
});
