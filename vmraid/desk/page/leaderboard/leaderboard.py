# Copyright (c) 2017, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals, print_function
import vmraid

@vmraid.whitelist()
def get_leaderboard_config():
	leaderboard_config = vmraid._dict()
	leaderboard_hooks = vmraid.get_hooks('leaderboards')
	for hook in leaderboard_hooks:
		leaderboard_config.update(vmraid.get_attr(hook)())

	return leaderboard_config