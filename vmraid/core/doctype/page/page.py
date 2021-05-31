# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import vmraid
import os
from vmraid.model.document import Document
from vmraid.build import html_to_js_template
from vmraid.model.utils import render_include
from vmraid import conf, _, safe_decode
from vmraid.desk.form.meta import get_code_files_via_hooks, get_js
from vmraid.desk.utils import validate_route_conflict
from vmraid.core.doctype.custom_role.custom_role import get_custom_allowed_roles
from six import text_type

class Page(Document):
	def autoname(self):
		"""
			Creates a url friendly name for this page.
			Will restrict the name to 30 characters, if there exists a similar name,
			it will add name-1, name-2 etc.
		"""
		from vmraid.utils import cint
		if (self.name and self.name.startswith('New Page')) or not self.name:
			self.name = self.page_name.lower().replace('"','').replace("'",'').\
				replace(' ', '-')[:20]
			if vmraid.db.exists('Page',self.name):
				cnt = vmraid.db.sql("""select name from tabPage
					where name like "%s-%%" order by name desc limit 1""" % self.name)
				if cnt:
					cnt = cint(cnt[0][0].split('-')[-1]) + 1
				else:
					cnt = 1
				self.name += '-' + str(cnt)

	def validate(self):
		validate_route_conflict(self.doctype, self.name)

		if self.is_new() and not getattr(conf,'developer_mode', 0):
			vmraid.throw(_("Not in Developer Mode"))

		#setting ignore_permissions via update_setup_wizard_access (setup_wizard.py)
		if vmraid.session.user!="Administrator" and not self.flags.ignore_permissions:
			vmraid.throw(_("Only Administrator can edit"))

	# export
	def on_update(self):
		"""
			Writes the .json for this page and if write_content is checked,
			it will write out a .html file
		"""
		if self.flags.do_not_update_json:
			return

		from vmraid.core.doctype.doctype.doctype import make_module_and_roles
		make_module_and_roles(self, "roles")

		from vmraid.modules.utils import export_module_json
		path = export_module_json(self, self.standard=='Yes', self.module)

		if path:
			# js
			if not os.path.exists(path + '.js'):
				with open(path + '.js', 'w') as f:
					f.write("""vmraid.pages['%s'].on_page_load = function(wrapper) {
	var page = vmraid.ui.make_app_page({
		parent: wrapper,
		title: '%s',
		single_column: true
	});
}""" % (self.name, self.title))

	def as_dict(self, no_nulls=False):
		d = super(Page, self).as_dict(no_nulls=no_nulls)
		for key in ("script", "style", "content"):
			d[key] = self.get(key)
		return d

	def on_trash(self):
		delete_custom_role('page', self.name)

	def is_permitted(self):
		"""Returns true if Has Role is not set or the user is allowed."""
		from vmraid.utils import has_common

		allowed = [d.role for d in vmraid.get_all("Has Role", fields=["role"],
			filters={"parent": self.name})]

		custom_roles = get_custom_allowed_roles('page', self.name)
		allowed.extend(custom_roles)

		if not allowed:
			return True

		roles = vmraid.get_roles()

		if has_common(roles, allowed):
			return True

	def load_assets(self):
		from vmraid.modules import get_module_path, scrub
		import os
		self.script = ''

		page_name = scrub(self.name)

		path = os.path.join(get_module_path(self.module), 'page', page_name)

		# script
		fpath = os.path.join(path, page_name + '.js')
		if os.path.exists(fpath):
			with open(fpath, 'r') as f:
				self.script = render_include(f.read())

		# css
		fpath = os.path.join(path, page_name + '.css')
		if os.path.exists(fpath):
			with open(fpath, 'r') as f:
				self.style = safe_decode(f.read())

		# html as js template
		for fname in os.listdir(path):
			if fname.endswith(".html"):
				with open(os.path.join(path, fname), 'r') as f:
					template = f.read()
					if "<!-- jinja -->" in template:
						context = vmraid._dict({})
						try:
							out = vmraid.get_attr("{app}.{module}.page.{page}.{page}.get_context".format(
								app = vmraid.local.module_app[scrub(self.module)],
								module = scrub(self.module),
								page = page_name
							))(context)

							if out:
								context = out
						except (AttributeError, ImportError):
							pass

						template = vmraid.render_template(template, context)
					self.script = html_to_js_template(fname, template) + self.script

					# flag for not caching this page
					self._dynamic_page = True

		if vmraid.lang != 'en':
			from vmraid.translate import get_lang_js
			self.script += get_lang_js("page", self.name)

		for path in get_code_files_via_hooks("page_js", self.name):
			js = get_js(path)
			if js:
				self.script += "\n\n" + js

def delete_custom_role(field, docname):
	name = vmraid.db.get_value('Custom Role', {field: docname}, "name")
	if name:
		vmraid.delete_doc('Custom Role', name)
