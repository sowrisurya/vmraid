from __future__ import unicode_literals
import vmraid
from vmraid import _
import vmraid.www.list

no_cache = 1

def get_context(context):
	if vmraid.session.user == 'Guest':
		vmraid.throw(_("You need to be logged in to access this page"), vmraid.PermissionError)

	active_tokens = vmraid.get_all("OAuth Bearer Token",
							filters=[["user", "=", vmraid.session.user]],
							fields=["client"], distinct=True, order_by="creation")

	client_apps = []

	for token in active_tokens:
		creation = get_first_login(token.client)
		app = {
			"name": token.get("client"),
			"app_name": vmraid.db.get_value("OAuth Client", token.get("client"), "app_name"),
			"creation": creation
		}
		client_apps.append(app)

	app = None
	if "app" in vmraid.form_dict:
		app = vmraid.get_doc("OAuth Client", vmraid.form_dict.app)
		app = app.__dict__
		app["client_secret"] = None

	if app:
		context.app = app

	context.apps = client_apps
	context.show_sidebar = True

def get_first_login(client):
	login_date = vmraid.get_all("OAuth Bearer Token",
		filters=[["user", "=", vmraid.session.user], ["client", "=", client]],
		fields=["creation"], order_by="creation", limit=1)

	login_date = login_date[0].get("creation") if login_date and len(login_date) > 0 else None

	return login_date

@vmraid.whitelist()
def delete_client(client_id):
	active_client_id_tokens = vmraid.get_all("OAuth Bearer Token", filters=[["user", "=", vmraid.session.user], ["client","=", client_id]])
	for token in active_client_id_tokens:
		vmraid.delete_doc("OAuth Bearer Token", token.get("name"),  ignore_permissions=True)