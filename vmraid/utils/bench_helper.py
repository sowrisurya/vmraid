from __future__ import unicode_literals, print_function
import click
import vmraid
import os
import json
import importlib
import vmraid.utils
import traceback
import warnings

click.disable_unicode_literals_warning = True

def main():
	commands = get_app_groups()
	commands.update({
		'get-vmraid-commands': get_vmraid_commands,
		'get-vmraid-help': get_vmraid_help
	})
	click.Group(commands=commands)(prog_name='bench')

def get_app_groups():
	'''Get all app groups, put them in main group "vmraid" since bench is
	designed to only handle that'''
	commands = dict()
	for app in get_apps():
		app_commands = get_app_commands(app)
		if app_commands:
			commands.update(app_commands)

	ret = dict(vmraid=click.group(name='vmraid', commands=commands)(app_group))
	return ret

def get_app_group(app):
	app_commands = get_app_commands(app)
	if app_commands:
		return click.group(name=app, commands=app_commands)(app_group)

@click.option('--site')
@click.option('--profile', is_flag=True, default=False, help='Profile')
@click.option('--verbose', is_flag=True, default=False, help='Verbose')
@click.option('--force', is_flag=True, default=False, help='Force')
@click.pass_context
def app_group(ctx, site=False, force=False, verbose=False, profile=False):
	ctx.obj = {
		'sites': get_sites(site),
		'force': force,
		'verbose': verbose,
		'profile': profile
	}
	if ctx.info_name == 'vmraid':
		ctx.info_name = ''

def get_sites(site_arg):
	if site_arg == 'all':
		return vmraid.utils.get_sites()
	elif site_arg:
		return [site_arg]
	elif os.environ.get('VMRAID_SITE'):
		return [os.environ.get('VMRAID_SITE')]
	elif os.path.exists('currentsite.txt'):
		with open('currentsite.txt') as f:
			site = f.read().strip()
			if site:
				return [site]
	return []

def get_app_commands(app):
	if os.path.exists(os.path.join('..', 'apps', app, app, 'commands.py'))\
		or os.path.exists(os.path.join('..', 'apps', app, app, 'commands', '__init__.py')):
		try:
			app_command_module = importlib.import_module(app + '.commands')
		except Exception:
			traceback.print_exc()
			return []
	else:
		return []

	ret = {}
	for command in getattr(app_command_module, 'commands', []):
		ret[command.name] = command
	return ret

@click.command('get-vmraid-commands')
def get_vmraid_commands():
	commands = list(get_app_commands('vmraid'))

	for app in get_apps():
		app_commands = get_app_commands(app)
		if app_commands:
			commands.extend(list(app_commands))

	print(json.dumps(commands))

@click.command('get-vmraid-help')
def get_vmraid_help():
	print(click.Context(get_app_groups()['vmraid']).get_help())

def get_apps():
	return vmraid.get_all_apps(with_internal_apps=False, sites_path='.')

if __name__ == "__main__":
	if not vmraid._dev_server:
		warnings.simplefilter('ignore')
	main()
