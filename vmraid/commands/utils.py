# -*- coding: utf-8 -*-

import json
import os
import subprocess
import sys
from distutils.spawn import find_executable

import click

import vmraid
from vmraid.commands import get_site, pass_context
from vmraid.exceptions import SiteNotSpecifiedError
from vmraid.utils import get_bench_path, update_progress_bar, cint


@click.command('build')
@click.option('--app', help='Build assets for app')
@click.option('--apps', help='Build assets for specific apps')
@click.option('--hard-link', is_flag=True, default=False, help='Copy the files instead of symlinking')
@click.option('--make-copy', is_flag=True, default=False, help='[DEPRECATED] Copy the files instead of symlinking')
@click.option('--restore', is_flag=True, default=False, help='[DEPRECATED] Copy the files instead of symlinking with force')
@click.option('--production', is_flag=True, default=False, help='Build assets in production mode')
@click.option('--verbose', is_flag=True, default=False, help='Verbose')
@click.option('--force', is_flag=True, default=False, help='Force build assets instead of downloading available')
def build(app=None, apps=None, hard_link=False, make_copy=False, restore=False, production=False, verbose=False, force=False):
	"Compile JS and CSS source files"
	from vmraid.build import bundle, download_vmraid_assets
	vmraid.init('')

	if not apps and app:
		apps = app

	# dont try downloading assets if force used, app specified or running via CI
	if not (force or apps or os.environ.get('CI')):
		# skip building vmraid if assets exist remotely
		skip_vmraid = download_vmraid_assets(verbose=verbose)
	else:
		skip_vmraid = False

	# don't minify in developer_mode for faster builds
	development = vmraid.local.conf.developer_mode or vmraid.local.dev_server
	mode = "development" if development else "production"
	if production:
		mode = "production"

	if make_copy or restore:
		hard_link = make_copy or restore
		click.secho(
			"bench build: --make-copy and --restore options are deprecated in favour of --hard-link",
			fg="yellow",
		)

	bundle(mode, apps=apps, hard_link=hard_link, verbose=verbose, skip_vmraid=skip_vmraid)



@click.command('watch')
@click.option('--apps', help='Watch assets for specific apps')
def watch(apps=None):
	"Watch and compile JS and CSS files as and when they change"
	from vmraid.build import watch
	vmraid.init('')
	watch(apps)


@click.command('clear-cache')
@pass_context
def clear_cache(context):
	"Clear cache, doctype cache and defaults"
	import vmraid.sessions
	import vmraid.website.render
	from vmraid.desk.notifications import clear_notifications
	for site in context.sites:
		try:
			vmraid.connect(site)
			vmraid.clear_cache()
			clear_notifications()
			vmraid.website.render.clear_cache()
		finally:
			vmraid.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError

@click.command('clear-website-cache')
@pass_context
def clear_website_cache(context):
	"Clear website cache"
	import vmraid.website.render
	for site in context.sites:
		try:
			vmraid.init(site=site)
			vmraid.connect()
			vmraid.website.render.clear_cache()
		finally:
			vmraid.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError

@click.command('destroy-all-sessions')
@click.option('--reason')
@pass_context
def destroy_all_sessions(context, reason=None):
	"Clear sessions of all users (logs them out)"
	import vmraid.sessions
	for site in context.sites:
		try:
			vmraid.init(site=site)
			vmraid.connect()
			vmraid.sessions.clear_all_sessions(reason)
			vmraid.db.commit()
		finally:
			vmraid.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError

@click.command('show-config')
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
@pass_context
def show_config(context, format):
	"Print configuration file to STDOUT in speified format"

	if not context.sites:
		raise SiteNotSpecifiedError

	sites_config = {}
	sites_path = os.getcwd()

	from vmraid.utils.commands import render_table

	def transform_config(config, prefix=None):
		prefix = f"{prefix}." if prefix else ""
		site_config = []

		for conf, value in config.items():
			if isinstance(value, dict):
				site_config += transform_config(value, prefix=f"{prefix}{conf}")
			else:
				log_value = json.dumps(value) if isinstance(value, list) else value
				site_config += [[f"{prefix}{conf}", log_value]]

		return site_config

	for site in context.sites:
		vmraid.init(site)

		if len(context.sites) != 1 and format == "text":
			if context.sites.index(site) != 0:
				click.echo()
			click.secho(f"Site {site}", fg="yellow")

		configuration = vmraid.get_site_config(sites_path=sites_path, site_path=site)

		if format == "text":
			data = transform_config(configuration)
			data.insert(0, ['Config','Value'])
			render_table(data)

		if format == "json":
			sites_config[site] = configuration

		vmraid.destroy()

	if format == "json":
		click.echo(vmraid.as_json(sites_config))


@click.command('reset-perms')
@pass_context
def reset_perms(context):
	"Reset permissions for all doctypes"
	from vmraid.permissions import reset_perms
	for site in context.sites:
		try:
			vmraid.init(site=site)
			vmraid.connect()
			for d in vmraid.db.sql_list("""select name from `tabDocType`
				where istable=0 and custom=0"""):
					vmraid.clear_cache(doctype=d)
					reset_perms(d)
		finally:
			vmraid.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError

@click.command('execute')
@click.argument('method')
@click.option('--args')
@click.option('--kwargs')
@click.option('--profile', is_flag=True, default=False)
@pass_context
def execute(context, method, args=None, kwargs=None, profile=False):
	"Execute a function"
	for site in context.sites:
		ret = ""
		try:
			vmraid.init(site=site)
			vmraid.connect()

			if args:
				try:
					args = eval(args)
				except NameError:
					args = [args]
			else:
				args = ()

			if kwargs:
				kwargs = eval(kwargs)
			else:
				kwargs = {}

			if profile:
				import cProfile
				pr = cProfile.Profile()
				pr.enable()

			try:
				ret = vmraid.get_attr(method)(*args, **kwargs)
			except Exception:
				ret = vmraid.safe_eval(method + "(*args, **kwargs)", eval_globals=globals(), eval_locals=locals())

			if profile:
				import pstats
				from six import StringIO

				pr.disable()
				s = StringIO()
				pstats.Stats(pr, stream=s).sort_stats('cumulative').print_stats(.5)
				print(s.getvalue())

			if vmraid.db:
				vmraid.db.commit()
		finally:
			vmraid.destroy()
		if ret:
			from vmraid.utils.response import json_handler
			print(json.dumps(ret, default=json_handler))

	if not context.sites:
		raise SiteNotSpecifiedError


@click.command('add-to-email-queue')
@click.argument('email-path')
@pass_context
def add_to_email_queue(context, email_path):
	"Add an email to the Email Queue"
	site = get_site(context)

	if os.path.isdir(email_path):
		with vmraid.init_site(site):
			vmraid.connect()
			for email in os.listdir(email_path):
				with open(os.path.join(email_path, email)) as email_data:
					kwargs = json.load(email_data)
					kwargs['delayed'] = True
					vmraid.sendmail(**kwargs)
					vmraid.db.commit()


@click.command('export-doc')
@click.argument('doctype')
@click.argument('docname')
@pass_context
def export_doc(context, doctype, docname):
	"Export a single document to csv"
	import vmraid.modules
	for site in context.sites:
		try:
			vmraid.init(site=site)
			vmraid.connect()
			vmraid.modules.export_doc(doctype, docname)
		finally:
			vmraid.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError

@click.command('export-json')
@click.argument('doctype')
@click.argument('path')
@click.option('--name', help='Export only one document')
@pass_context
def export_json(context, doctype, path, name=None):
	"Export doclist as json to the given path, use '-' as name for Singles."
	from vmraid.core.doctype.data_import.data_import import export_json
	for site in context.sites:
		try:
			vmraid.init(site=site)
			vmraid.connect()
			export_json(doctype, path, name=name)
		finally:
			vmraid.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError

@click.command('export-csv')
@click.argument('doctype')
@click.argument('path')
@pass_context
def export_csv(context, doctype, path):
	"Export data import template with data for DocType"
	from vmraid.core.doctype.data_import.data_import import export_csv
	for site in context.sites:
		try:
			vmraid.init(site=site)
			vmraid.connect()
			export_csv(doctype, path)
		finally:
			vmraid.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError

@click.command('export-fixtures')
@click.option('--app', default=None, help='Export fixtures of a specific app')
@pass_context
def export_fixtures(context, app=None):
	"Export fixtures"
	from vmraid.utils.fixtures import export_fixtures
	for site in context.sites:
		try:
			vmraid.init(site=site)
			vmraid.connect()
			export_fixtures(app=app)
		finally:
			vmraid.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError

@click.command('import-doc')
@click.argument('path')
@pass_context
def import_doc(context, path, force=False):
	"Import (insert/update) doclist. If the argument is a directory, all files ending with .json are imported"
	from vmraid.core.doctype.data_import.data_import import import_doc

	if not os.path.exists(path):
		path = os.path.join('..', path)
	if not os.path.exists(path):
		print('Invalid path {0}'.format(path))
		sys.exit(1)

	for site in context.sites:
		try:
			vmraid.init(site=site)
			vmraid.connect()
			import_doc(path)
		finally:
			vmraid.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError

@click.command('import-csv')
@click.argument('path')
@click.option('--only-insert', default=False, is_flag=True, help='Do not overwrite existing records')
@click.option('--submit-after-import', default=False, is_flag=True, help='Submit document after importing it')
@click.option('--ignore-encoding-errors', default=False, is_flag=True, help='Ignore encoding errors while coverting to unicode')
@click.option('--no-email', default=True, is_flag=True, help='Send email if applicable')
@pass_context
def import_csv(context, path, only_insert=False, submit_after_import=False, ignore_encoding_errors=False, no_email=True):
	"Import CSV using data import"
	from vmraid.core.doctype.data_import_legacy import importer
	from vmraid.utils.csvutils import read_csv_content
	site = get_site(context)

	if not os.path.exists(path):
		path = os.path.join('..', path)
	if not os.path.exists(path):
		print('Invalid path {0}'.format(path))
		sys.exit(1)

	with open(path, 'r') as csvfile:
		content = read_csv_content(csvfile.read())

	vmraid.init(site=site)
	vmraid.connect()

	try:
		importer.upload(content, submit_after_import=submit_after_import, no_email=no_email,
			ignore_encoding_errors=ignore_encoding_errors, overwrite=not only_insert,
			via_console=True)
		vmraid.db.commit()
	except Exception:
		print(vmraid.get_traceback())

	vmraid.destroy()


@click.command('data-import')
@click.option('--file', 'file_path', type=click.Path(), required=True, help="Path to import file (.csv, .xlsx)")
@click.option('--doctype', type=str, required=True)
@click.option('--type', 'import_type', type=click.Choice(['Insert', 'Update'], case_sensitive=False), default='Insert', help="Insert New Records or Update Existing Records")
@click.option('--submit-after-import', default=False, is_flag=True, help='Submit document after importing it')
@click.option('--mute-emails', default=True, is_flag=True, help='Mute emails during import')
@pass_context
def data_import(context, file_path, doctype, import_type=None, submit_after_import=False, mute_emails=True):
	"Import documents in bulk from CSV or XLSX using data import"
	from vmraid.core.doctype.data_import.data_import import import_file
	site = get_site(context)

	vmraid.init(site=site)
	vmraid.connect()
	import_file(doctype, file_path, import_type, submit_after_import, console=True)
	vmraid.destroy()


@click.command('bulk-rename')
@click.argument('doctype')
@click.argument('path')
@pass_context
def bulk_rename(context, doctype, path):
	"Rename multiple records via CSV file"
	from vmraid.model.rename_doc import bulk_rename
	from vmraid.utils.csvutils import read_csv_content

	site = get_site(context)

	with open(path, 'r') as csvfile:
		rows = read_csv_content(csvfile.read())

	vmraid.init(site=site)
	vmraid.connect()

	bulk_rename(doctype, rows, via_console = True)

	vmraid.destroy()


@click.command('mariadb')
@pass_context
def mariadb(context):
	"""
		Enter into mariadb console for a given site.
	"""
	import os

	site  = get_site(context)
	if not site:
		raise SiteNotSpecifiedError
	vmraid.init(site=site)

	# This is assuming you're within the bench instance.
	mysql = find_executable('mysql')
	os.execv(mysql, [
		mysql,
		'-u', vmraid.conf.db_name,
		'-p'+vmraid.conf.db_password,
		vmraid.conf.db_name,
		'-h', vmraid.conf.db_host or "localhost",
		'--pager=less -SFX',
		'--safe-updates',
		"-A"])


@click.command('postgres')
@pass_context
def postgres(context):
	"""
		Enter into postgres console for a given site.
	"""
	site  = get_site(context)
	vmraid.init(site=site)
	# This is assuming you're within the bench instance.
	psql = find_executable('psql')
	subprocess.run([ psql, '-d', vmraid.conf.db_name])


@click.command('jupyter')
@pass_context
def jupyter(context):
	installed_packages = (r.split('==')[0] for r in subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], encoding='utf8'))

	if 'jupyter' not in installed_packages:
		subprocess.check_output([sys.executable, '-m', 'pip', 'install', 'jupyter'])

	site = get_site(context)
	vmraid.init(site=site)

	jupyter_notebooks_path = os.path.abspath(vmraid.get_site_path('jupyter_notebooks'))
	sites_path = os.path.abspath(vmraid.get_site_path('..'))

	try:
		os.stat(jupyter_notebooks_path)
	except OSError:
		print('Creating folder to keep jupyter notebooks at {}'.format(jupyter_notebooks_path))
		os.mkdir(jupyter_notebooks_path)
	bin_path = os.path.abspath('../env/bin')
	print('''
Starting Jupyter notebook
Run the following in your first cell to connect notebook to vmraid
```
import vmraid
vmraid.init(site='{site}', sites_path='{sites_path}')
vmraid.connect()
vmraid.local.lang = vmraid.db.get_default('lang')
vmraid.db.connect()
```
	'''.format(site=site, sites_path=sites_path))
	os.execv('{0}/jupyter'.format(bin_path), [
		'{0}/jupyter'.format(bin_path),
		'notebook',
		jupyter_notebooks_path,
	])


@click.command('console')
@pass_context
def console(context):
	"Start ipython console for a site"
	site = get_site(context)
	vmraid.init(site=site)
	vmraid.connect()
	vmraid.local.lang = vmraid.db.get_default("lang")

	import IPython
	all_apps = vmraid.get_installed_apps()
	failed_to_import = []

	for app in all_apps:
		try:
			locals()[app] = __import__(app)
		except ModuleNotFoundError:
			failed_to_import.append(app)
			all_apps.remove(app)

	print("Apps in this namespace:\n{}".format(", ".join(all_apps)))
	if failed_to_import:
		print("\nFailed to import:\n{}".format(", ".join(failed_to_import)))

	IPython.embed(display_banner="", header="", colors="neutral")


@click.command('run-tests')
@click.option('--app', help="For App")
@click.option('--doctype', help="For DocType")
@click.option('--doctype-list-path', help="Path to .txt file for list of doctypes. Example erpadda/tests/server/agriculture.txt")
@click.option('--test', multiple=True, help="Specific test")
@click.option('--ui-tests', is_flag=True, default=False, help="Run UI Tests")
@click.option('--module', help="Run tests in a module")
@click.option('--profile', is_flag=True, default=False)
@click.option('--coverage', is_flag=True, default=False)
@click.option('--skip-test-records', is_flag=True, default=False, help="Don't create test records")
@click.option('--skip-before-tests', is_flag=True, default=False, help="Don't run before tests hook")
@click.option('--junit-xml-output', help="Destination file path for junit xml report")
@click.option('--failfast', is_flag=True, default=False)
@pass_context
def run_tests(context, app=None, module=None, doctype=None, test=(), profile=False,
		coverage=False, junit_xml_output=False, ui_tests = False, doctype_list_path=None,
		skip_test_records=False, skip_before_tests=False, failfast=False):

	"Run tests"
	import vmraid.test_runner
	tests = test

	site = get_site(context)

	allow_tests = vmraid.get_conf(site).allow_tests

	if not (allow_tests or os.environ.get('CI')):
		click.secho('Testing is disabled for the site!', bold=True)
		click.secho('You can enable tests by entering following command:')
		click.secho('bench --site {0} set-config allow_tests true'.format(site), fg='green')
		return

	vmraid.init(site=site)

	vmraid.flags.skip_before_tests = skip_before_tests
	vmraid.flags.skip_test_records = skip_test_records

	if coverage:
		from coverage import Coverage

		# Generate coverage report only for app that is being tested
		source_path = os.path.join(get_bench_path(), 'apps', app or 'vmraid')
		omit=[
			'*.html',
			'*.js',
			'*.xml',
			'*.css',
			'*.less',
			'*.scss',
			'*.vue',
			'*/doctype/*/*_dashboard.py',
			'*/patches/*'
		]

		if not app or app == 'vmraid':
			omit.append('*/commands/*')

		cov = Coverage(source=[source_path], omit=omit)
		cov.start()

	ret = vmraid.test_runner.main(app, module, doctype, context.verbose, tests=tests,
		force=context.force, profile=profile, junit_xml_output=junit_xml_output,
		ui_tests=ui_tests, doctype_list_path=doctype_list_path, failfast=failfast)

	if coverage:
		cov.stop()
		cov.save()

	if len(ret.failures) == 0 and len(ret.errors) == 0:
		ret = 0

	if os.environ.get('CI'):
		sys.exit(ret)

@click.command('run-parallel-tests')
@click.option('--app', help="For App", default='vmraid')
@click.option('--build-number', help="Build number", default=1)
@click.option('--total-builds', help="Total number of builds", default=1)
@click.option('--with-coverage', is_flag=True, help="Build coverage file")
@click.option('--use-orchestrator', is_flag=True, help="Use orchestrator to run parallel tests")
@pass_context
def run_parallel_tests(context, app, build_number, total_builds, with_coverage=False, use_orchestrator=False):
	site = get_site(context)
	if use_orchestrator:
		from vmraid.parallel_test_runner import ParallelTestWithOrchestrator
		ParallelTestWithOrchestrator(app, site=site, with_coverage=with_coverage)
	else:
		from vmraid.parallel_test_runner import ParallelTestRunner
		ParallelTestRunner(app, site=site, build_number=build_number, total_builds=total_builds, with_coverage=with_coverage)

@click.command('run-ui-tests')
@click.argument('app')
@click.option('--headless', is_flag=True, help="Run UI Test in headless mode")
@click.option('--parallel', is_flag=True, help="Run UI Test in parallel mode")
@click.option('--ci-build-id')
@pass_context
def run_ui_tests(context, app, headless=False, parallel=True, ci_build_id=None):
	"Run UI tests"
	site = get_site(context)
	app_base_path = os.path.abspath(os.path.join(vmraid.get_app_path(app), '..'))
	site_url = vmraid.utils.get_site_url(site)
	admin_password = vmraid.get_conf(site).admin_password

	# override baseUrl using env variable
	site_env = 'CYPRESS_baseUrl={}'.format(site_url)
	password_env = 'CYPRESS_adminPassword={}'.format(admin_password) if admin_password else ''

	os.chdir(app_base_path)

	node_bin = subprocess.getoutput("npm bin")
	cypress_path = "{0}/cypress".format(node_bin)
	plugin_path = "{0}/../cypress-file-upload".format(node_bin)

	# check if cypress in path...if not, install it.
	if not (
		os.path.exists(cypress_path)
		and os.path.exists(plugin_path)
		and cint(subprocess.getoutput("npm view cypress version")[:1]) >= 6
	):
		# install cypress
		click.secho("Installing Cypress...", fg="yellow")
		vmraid.commands.popen("yarn add cypress@^6 cypress-file-upload@^5 --no-lockfile")

	# run for headless mode
	run_or_open = 'run --browser firefox --record --key 4a48f41c-11b3-425b-aa88-c58048fa69eb' if headless else 'open'
	command = '{site_env} {password_env} {cypress} {run_or_open}'
	formatted_command = command.format(site_env=site_env, password_env=password_env, cypress=cypress_path, run_or_open=run_or_open)

	if parallel:
		formatted_command += ' --parallel'

	if ci_build_id:
		formatted_command += ' --ci-build-id {}'.format(ci_build_id)

	click.secho("Running Cypress...", fg="yellow")
	vmraid.commands.popen(formatted_command, cwd=app_base_path, raise_err=True)


@click.command('serve')
@click.option('--port', default=8000)
@click.option('--profile', is_flag=True, default=False)
@click.option('--noreload', "no_reload", is_flag=True, default=False)
@click.option('--nothreading', "no_threading", is_flag=True, default=False)
@pass_context
def serve(context, port=None, profile=False, no_reload=False, no_threading=False, sites_path='.', site=None):
	"Start development web server"
	import vmraid.app

	if not context.sites:
		site = None
	else:
		site = context.sites[0]

	vmraid.app.serve(port=port, profile=profile, no_reload=no_reload, no_threading=no_threading, site=site, sites_path='.')


@click.command('request')
@click.option('--args', help='arguments like `?cmd=test&key=value` or `/api/request/method?..`')
@click.option('--path', help='path to request JSON')
@pass_context
def request(context, args=None, path=None):
	"Run a request as an admin"
	import vmraid.handler
	import vmraid.api
	for site in context.sites:
		try:
			vmraid.init(site=site)
			vmraid.connect()
			if args:
				if "?" in args:
					vmraid.local.form_dict = vmraid._dict([a.split("=") for a in args.split("?")[-1].split("&")])
				else:
					vmraid.local.form_dict = vmraid._dict()

				if args.startswith("/api/method"):
					vmraid.local.form_dict.cmd = args.split("?")[0].split("/")[-1]
			elif path:
				with open(os.path.join('..', path), 'r') as f:
					args = json.loads(f.read())

				vmraid.local.form_dict = vmraid._dict(args)

			vmraid.handler.execute_cmd(vmraid.form_dict.cmd)

			print(vmraid.response)
		finally:
			vmraid.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError

@click.command('make-app')
@click.argument('destination')
@click.argument('app_name')
def make_app(destination, app_name):
	"Creates a boilerplate app"
	from vmraid.utils.boilerplate import make_boilerplate
	make_boilerplate(destination, app_name)


@click.command('set-config')
@click.argument('key')
@click.argument('value')
@click.option('-g', '--global', 'global_', is_flag=True, default=False, help='Set value in bench config')
@click.option('-p', '--parse', is_flag=True, default=False, help='Evaluate as Python Object')
@click.option('--as-dict', is_flag=True, default=False, help='Legacy: Evaluate as Python Object')
@pass_context
def set_config(context, key, value, global_=False, parse=False, as_dict=False):
	"Insert/Update a value in site_config.json"
	from vmraid.installer import update_site_config

	if as_dict:
		from vmraid.utils.commands import warn
		warn("--as-dict will be deprecated in v14. Use --parse instead", category=PendingDeprecationWarning)
		parse = as_dict

	if parse:
		import ast
		value = ast.literal_eval(value)

	if global_:
		sites_path = os.getcwd()
		common_site_config_path = os.path.join(sites_path, 'common_site_config.json')
		update_site_config(key, value, validate=False, site_config_path=common_site_config_path)
	else:
		for site in context.sites:
			vmraid.init(site=site)
			update_site_config(key, value, validate=False)
			vmraid.destroy()


@click.command('version')
def get_version():
	"Show the versions of all the installed apps"
	from vmraid.utils.change_log import get_app_branch
	vmraid.init('')

	for m in sorted(vmraid.get_all_apps()):
		branch_name = get_app_branch(m)
		module = vmraid.get_module(m)
		app_hooks = vmraid.get_module(m + ".hooks")

		if hasattr(app_hooks, '{0}_version'.format(branch_name)):
			print("{0} {1}".format(m, getattr(app_hooks, '{0}_version'.format(branch_name))))

		elif hasattr(module, "__version__"):
			print("{0} {1}".format(m, module.__version__))


@click.command('rebuild-global-search')
@click.option('--static-pages', is_flag=True, default=False, help='Rebuild global search for static pages')
@pass_context
def rebuild_global_search(context, static_pages=False):
	'''Setup help table in the current site (called after migrate)'''
	from vmraid.utils.global_search import (get_doctypes_with_global_search, rebuild_for_doctype,
		get_routes_to_index, add_route_to_global_search, sync_global_search)

	for site in context.sites:
		try:
			vmraid.init(site)
			vmraid.connect()

			if static_pages:
				routes = get_routes_to_index()
				for i, route in enumerate(routes):
					add_route_to_global_search(route)
					vmraid.local.request = None
					update_progress_bar('Rebuilding Global Search', i, len(routes))
				sync_global_search()
			else:
				doctypes = get_doctypes_with_global_search()
				for i, doctype in enumerate(doctypes):
					rebuild_for_doctype(doctype)
					update_progress_bar('Rebuilding Global Search', i, len(doctypes))

		finally:
			vmraid.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


commands = [
	build,
	clear_cache,
	clear_website_cache,
	jupyter,
	console,
	destroy_all_sessions,
	execute,
	export_csv,
	export_doc,
	export_fixtures,
	export_json,
	get_version,
	import_csv,
	data_import,
	import_doc,
	make_app,
	mariadb,
	postgres,
	request,
	reset_perms,
	run_tests,
	run_ui_tests,
	serve,
	set_config,
	show_config,
	watch,
	bulk_rename,
	add_to_email_queue,
	rebuild_global_search,
	run_parallel_tests
]
