# -*- coding: utf-8 -*-
# Copyright (c) 2019, VMRaid Technologies and contributors
# For license information, please see license.txt

import os
from urllib.parse import urljoin
from urllib.parse import urlencode

import vmraid
from vmraid import _
from vmraid.model.document import Document
from requests_oauthlib import OAuth2Session

if any((os.getenv('CI'), vmraid.conf.developer_mode, vmraid.conf.allow_tests)):
	# Disable mandatory TLS in developer mode and tests
	os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

class ConnectedApp(Document):
	"""Connect to a remote oAuth Server. Retrieve and store user's access token
	in a Token Cache.
	"""

	def validate(self):
		base_url = vmraid.utils.get_url()
		callback_path = '/api/method/vmraid.integrations.doctype.connected_app.connected_app.callback/' + self.name
		self.redirect_uri = urljoin(base_url, callback_path)

	def get_oauth2_session(self, user=None, init=False):
		"""Return an auto-refreshing OAuth2 session which is an extension of a requests.Session()"""
		token = None
		token_updater = None
		auto_refresh_kwargs = None

		if not init:
			user = user or vmraid.session.user
			token_cache = self.get_user_token(user)
			token = token_cache.get_json()
			token_updater = token_cache.update_data
			auto_refresh_kwargs = {'client_id': self.client_id}
			client_secret = self.get_password('client_secret')
			if client_secret:
				auto_refresh_kwargs['client_secret'] = client_secret

		return OAuth2Session(
			client_id=self.client_id,
			token=token,
			token_updater=token_updater,
			auto_refresh_url=self.token_uri,
			auto_refresh_kwargs=auto_refresh_kwargs,
			redirect_uri=self.redirect_uri,
			scope=self.get_scopes()
		)

	@vmraid.whitelist()
	def initiate_web_application_flow(self, user=None, success_uri=None):
		"""Return an authorization URL for the user. Save state in Token Cache."""
		user = user or vmraid.session.user
		oauth = self.get_oauth2_session(init=True)
		query_params = self.get_query_params()
		authorization_url, state = oauth.authorization_url(self.authorization_uri, **query_params)
		token_cache = self.get_token_cache(user)

		if not token_cache:
			token_cache = vmraid.new_doc('Token Cache')
			token_cache.user = user
			token_cache.connected_app = self.name

		token_cache.success_uri = success_uri
		token_cache.state = state
		token_cache.save(ignore_permissions=True)
		vmraid.db.commit()

		return authorization_url

	def get_user_token(self, user=None, success_uri=None):
		"""Return an existing user token or initiate a Web Application Flow."""
		user = user or vmraid.session.user
		token_cache = self.get_token_cache(user)

		if token_cache:
			return token_cache

		redirect = self.initiate_web_application_flow(user, success_uri)
		vmraid.local.response['type'] = 'redirect'
		vmraid.local.response['location'] = redirect
		return redirect

	def get_token_cache(self, user):
		token_cache = None
		token_cache_name = self.name + '-' + user

		if vmraid.db.exists('Token Cache', token_cache_name):
			token_cache = vmraid.get_doc('Token Cache', token_cache_name)

		return token_cache

	def get_scopes(self):
		return [row.scope for row in self.scopes]

	def get_query_params(self):
		return {param.key: param.value for param in self.query_parameters}


@vmraid.whitelist(allow_guest=True)
def callback(code=None, state=None):
	"""Handle client's code.

	Called during the oauthorization flow by the remote oAuth2 server to
	transmit a code that can be used by the local server to obtain an access
	token.
	"""
	if vmraid.request.method != 'GET':
		vmraid.throw(_('Invalid request method: {}').format(vmraid.request.method))

	if vmraid.session.user == 'Guest':
		vmraid.local.response['type'] = 'redirect'
		vmraid.local.response['location'] = '/login?' + urlencode({'redirect-to': vmraid.request.url})
		return

	path = vmraid.request.path[1:].split('/')
	if len(path) != 4 or not path[3]:
		vmraid.throw(_('Invalid Parameters.'))

	connected_app = vmraid.get_doc('Connected App', path[3])
	token_cache = vmraid.get_doc('Token Cache', connected_app.name + '-' + vmraid.session.user)

	if state != token_cache.state:
		vmraid.throw(_('Invalid state.'))

	oauth_session = connected_app.get_oauth2_session(init=True)
	query_params = connected_app.get_query_params()
	token = oauth_session.fetch_token(connected_app.token_uri,
		code=code,
		client_secret=connected_app.get_password('client_secret'),
		include_client_id=True,
		**query_params
	)
	token_cache.update_data(token)

	vmraid.local.response['type'] = 'redirect'
	vmraid.local.response['location'] = token_cache.get('success_uri') or connected_app.get_url()
