# imports - standard imports
import sys

# imports - module imports
from vmraid.integrations.vmraid_providers.vmraidcloud import vmraidcloud_migrator


def migrate_to(local_site, vmraid_provider):
	if vmraid_provider in ("vmraid.cloud", "vmraidcloud.com"):
		return vmraidcloud_migrator(local_site)
	else:
		print("{} is not supported yet".format(vmraid_provider))
		sys.exit(1)
