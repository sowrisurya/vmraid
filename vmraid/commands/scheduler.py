from __future__ import unicode_literals, absolute_import, print_function
import click
import sys
import vmraid
from vmraid.utils import cint
from vmraid.commands import pass_context, get_site
from vmraid.exceptions import SiteNotSpecifiedError

def _is_scheduler_enabled():
	enable_scheduler = False
	try:
		vmraid.connect()
		enable_scheduler = cint(vmraid.db.get_single_value("System Settings", "enable_scheduler")) and True or False
	except:
		pass
	finally:
		vmraid.db.close()

	return enable_scheduler


@click.command("trigger-scheduler-event", help="Trigger a scheduler event")
@click.argument("event")
@pass_context
def trigger_scheduler_event(context, event):
	import vmraid.utils.scheduler

	exit_code = 0

	for site in context.sites:
		try:
			vmraid.init(site=site)
			vmraid.connect()
			try:
				vmraid.get_doc("Scheduled Job Type", {"method": event}).execute()
			except vmraid.DoesNotExistError:
				click.secho(f"Event {event} does not exist!", fg="red")
				exit_code = 1
		finally:
			vmraid.destroy()

	if not context.sites:
		raise SiteNotSpecifiedError

	sys.exit(exit_code)


@click.command('enable-scheduler')
@pass_context
def enable_scheduler(context):
	"Enable scheduler"
	import vmraid.utils.scheduler
	for site in context.sites:
		try:
			vmraid.init(site=site)
			vmraid.connect()
			vmraid.utils.scheduler.enable_scheduler()
			vmraid.db.commit()
			print("Enabled for", site)
		finally:
			vmraid.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError

@click.command('disable-scheduler')
@pass_context
def disable_scheduler(context):
	"Disable scheduler"
	import vmraid.utils.scheduler
	for site in context.sites:
		try:
			vmraid.init(site=site)
			vmraid.connect()
			vmraid.utils.scheduler.disable_scheduler()
			vmraid.db.commit()
			print("Disabled for", site)
		finally:
			vmraid.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


@click.command('scheduler')
@click.option('--site', help='site name')
@click.argument('state', type=click.Choice(['pause', 'resume', 'disable', 'enable']))
@pass_context
def scheduler(context, state, site=None):
	from vmraid.installer import update_site_config
	import vmraid.utils.scheduler

	if not site:
		site = get_site(context)

	try:
		vmraid.init(site=site)

		if state == 'pause':
			update_site_config('pause_scheduler', 1)
		elif state == 'resume':
			update_site_config('pause_scheduler', 0)
		elif state == 'disable':
			vmraid.connect()
			vmraid.utils.scheduler.disable_scheduler()
			vmraid.db.commit()
		elif state == 'enable':
			vmraid.connect()
			vmraid.utils.scheduler.enable_scheduler()
			vmraid.db.commit()

		print('Scheduler {0}d for site {1}'.format(state, site))

	finally:
		vmraid.destroy()


@click.command('set-maintenance-mode')
@click.option('--site', help='site name')
@click.argument('state', type=click.Choice(['on', 'off']))
@pass_context
def set_maintenance_mode(context, state, site=None):
	from vmraid.installer import update_site_config
	if not site:
		site = get_site(context)

	try:
		vmraid.init(site=site)
		update_site_config('maintenance_mode', 1 if (state == 'on') else 0)

	finally:
		vmraid.destroy()


@click.command('doctor') #Passing context always gets a site and if there is no use site it breaks
@click.option('--site', help='site name')
@pass_context
def doctor(context, site=None):
	"Get diagnostic info about background workers"
	from vmraid.utils.doctor import doctor as _doctor
	if not site:
		site = get_site(context, raise_err=False)
	return _doctor(site=site)

@click.command('show-pending-jobs')
@click.option('--site', help='site name')
@pass_context
def show_pending_jobs(context, site=None):
	"Get diagnostic info about background jobs"
	from vmraid.utils.doctor import pending_jobs as _pending_jobs
	if not site:
		site = get_site(context)

	with vmraid.init_site(site):
		pending_jobs = _pending_jobs(site=site)

	return pending_jobs

@click.command('purge-jobs')
@click.option('--site', help='site name')
@click.option('--queue', default=None, help='one of "low", "default", "high')
@click.option('--event', default=None, help='one of "all", "weekly", "monthly", "hourly", "daily", "weekly_long", "daily_long"')
def purge_jobs(site=None, queue=None, event=None):
	"Purge any pending periodic tasks, if event option is not given, it will purge everything for the site"
	from vmraid.utils.doctor import purge_pending_jobs
	vmraid.init(site or '')
	count = purge_pending_jobs(event=event, site=site, queue=queue)
	print("Purged {} jobs".format(count))

@click.command('schedule')
def start_scheduler():
	from vmraid.utils.scheduler import start_scheduler
	start_scheduler()

@click.command('worker')
@click.option('--queue', type=str)
@click.option('--quiet', is_flag = True, default = False, help = 'Hide Log Outputs')
def start_worker(queue, quiet = False):
	from vmraid.utils.background_jobs import start_worker
	start_worker(queue, quiet = quiet)

@click.command('ready-for-migration')
@click.option('--site', help='site name')
@pass_context
def ready_for_migration(context, site=None):
	from vmraid.utils.doctor import get_pending_jobs

	if not site:
		site = get_site(context)

	try:
		vmraid.init(site=site)
		pending_jobs = get_pending_jobs(site=site)

		if pending_jobs:
			print('NOT READY for migration: site {0} has pending background jobs'.format(site))
			sys.exit(1)

		else:
			print('READY for migration: site {0} does not have any background jobs'.format(site))
			return 0

	finally:
		vmraid.destroy()

commands = [
	disable_scheduler,
	doctor,
	enable_scheduler,
	purge_jobs,
	ready_for_migration,
	scheduler,
	set_maintenance_mode,
	show_pending_jobs,
	start_scheduler,
	start_worker,
	trigger_scheduler_event,
]
