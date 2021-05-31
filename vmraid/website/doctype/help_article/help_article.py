# Copyright (c) 2013, VMRaid and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import vmraid
from vmraid.website.website_generator import WebsiteGenerator
from vmraid.utils import is_markdown, markdown, cint
from vmraid.website.utils import get_comment_list
from vmraid import _

class HelpArticle(WebsiteGenerator):
	def validate(self):
		self.set_route()

	def set_route(self):
		'''Set route from category and title if missing'''
		if not self.route:
			self.route = '/'.join([vmraid.get_value('Help Category', self.category, 'route'),
				self.scrub(self.title)])

	def on_update(self):
		self.update_category()
		clear_cache()

	def update_category(self):
		cnt = vmraid.db.sql("""select count(*) from `tabHelp Article`
			where category=%s and ifnull(published,0)=1""", self.category)[0][0]
		cat = vmraid.get_doc("Help Category", self.category)
		cat.help_articles = cnt
		cat.save()

	def get_context(self, context):
		if is_markdown(context.content):
			context.content = markdown(context.content)
		context.login_required = True
		context.category = vmraid.get_doc('Help Category', self.category)
		context.level_class = get_level_class(self.level)
		context.comment_list = get_comment_list(self.doctype, self.name)
		context.show_sidebar = True
		context.sidebar_items = get_sidebar_items()
		context.parents = self.get_parents(context)

	def get_parents(self, context):
		return [{"title": context.category.category_name, "route":context.category.route}]

def get_list_context(context=None):
	filters = dict(published=1)

	category = vmraid.db.get_value("Help Category", { "route": vmraid.local.path })

	if category:
		filters['category'] = category

	list_context = vmraid._dict(
		title = category or _("Knowledge Base"),
		get_level_class = get_level_class,
		show_sidebar = True,
		sidebar_items = get_sidebar_items(),
		hide_filters = True,
		filters = filters,
		category = vmraid.local.form_dict.category,
		no_breadcrumbs = True
	)


	if vmraid.local.form_dict.txt:
		list_context.blog_subtitle = _('Filtered by "{0}"').format(vmraid.local.form_dict.txt)
	#
	# list_context.update(vmraid.get_doc("Blog Settings", "Blog Settings").as_dict())
	return list_context

def get_level_class(level):
	return {
		"Beginner": "green",
		"Intermediate": "orange",
		"Expert": "red"
	}[level]

def get_sidebar_items():
	def _get():
		return vmraid.db.sql("""select
				concat(category_name, " (", help_articles, ")") as title,
				concat('/', route) as route
			from
				`tabHelp Category`
			where
				ifnull(published,0)=1 and help_articles > 0
			order by
				help_articles desc""", as_dict=True)

	return vmraid.cache().get_value("knowledge_base:category_sidebar", _get)

def clear_cache():
	clear_website_cache()

	from vmraid.website.render import clear_cache
	clear_cache()

def clear_website_cache(path=None):
	vmraid.cache().delete_value("knowledge_base:category_sidebar")
	vmraid.cache().delete_value("knowledge_base:faq")

@vmraid.whitelist(allow_guest=True)
def add_feedback(article, helpful):
	field = "helpful"
	if helpful == "No":
		field = "not_helpful"

	value = cint(vmraid.db.get_value("Help Article", article, field))
	vmraid.db.set_value("Help Article", article, field, value+1, update_modified=False)