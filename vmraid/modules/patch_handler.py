# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals, print_function
"""
	Execute Patch Files

	To run directly

	python lib/wnf.py patch patch1, patch2 etc
	python lib/wnf.py patch -f patch1, patch2 etc

	where patch1, patch2 is module name
"""
import vmraid, vmraid.permissions, time

# for patches
import os

class PatchError(Exception): pass

def run_all(skip_failing=False):
	"""run all pending patches"""
	executed = [p[0] for p in vmraid.db.sql("""select patch from `tabPatch Log`""")]

	vmraid.flags.final_patches = []

	def run_patch(patch):
		try:
			if not run_single(patchmodule = patch):
				log(patch + ': failed: STOPPED')
				raise PatchError(patch)
		except Exception:
			if not skip_failing:
				raise
			else:
				log('Failed to execute patch')

	for patch in get_all_patches():
		if patch and (patch not in executed):
			run_patch(patch)

	# patches to be run in the end
	for patch in vmraid.flags.final_patches:
		patch = patch.replace('finally:', '')
		run_patch(patch)

def get_all_patches():
	patches = []
	for app in vmraid.get_installed_apps():
		if app == "shopping_cart":
			continue
		# 3-to-4 fix
		if app=="webnotes":
			app="vmraid"
		patches.extend(vmraid.get_file_items(vmraid.get_pymodule_path(app, "patches.txt")))

	return patches

def reload_doc(args):
	import vmraid.modules
	run_single(method = vmraid.modules.reload_doc, methodargs = args)

def run_single(patchmodule=None, method=None, methodargs=None, force=False):
	from vmraid import conf

	# don't write txt files
	conf.developer_mode = 0

	if force or method or not executed(patchmodule):
		return execute_patch(patchmodule, method, methodargs)
	else:
		return True

def execute_patch(patchmodule, method=None, methodargs=None):
	"""execute the patch"""
	block_user(True)
	vmraid.db.begin()
	start_time = time.time()
	try:
		log('Executing {patch} in {site} ({db})'.format(patch=patchmodule or str(methodargs),
			site=vmraid.local.site, db=vmraid.db.cur_db_name))
		if patchmodule:
			if patchmodule.startswith("finally:"):
				# run run patch at the end
				vmraid.flags.final_patches.append(patchmodule)
			else:
				if patchmodule.startswith("execute:"):
					exec(patchmodule.split("execute:")[1],globals())
				else:
					vmraid.get_attr(patchmodule.split()[0] + ".execute")()
				update_patch_log(patchmodule)
		elif method:
			method(**methodargs)

	except Exception:
		vmraid.db.rollback()
		raise

	else:
		vmraid.db.commit()
		end_time = time.time()
		block_user(False)
		log('Success: Done in {time}s'.format(time = round(end_time - start_time, 3)))

	return True

def update_patch_log(patchmodule):
	"""update patch_file in patch log"""
	vmraid.get_doc({"doctype": "Patch Log", "patch": patchmodule}).insert(ignore_permissions=True)

def executed(patchmodule):
	"""return True if is executed"""
	if patchmodule.startswith('finally:'):
		# patches are saved without the finally: tag
		patchmodule = patchmodule.replace('finally:', '')
	done = vmraid.db.get_value("Patch Log", {"patch": patchmodule})
	# if done:
	# 	print "Patch %s already executed in %s" % (patchmodule, vmraid.db.cur_db_name)
	return done

def block_user(block, msg=None):
	"""stop/start execution till patch is run"""
	vmraid.local.flags.in_patch = block
	vmraid.db.begin()
	if not msg:
		msg = "Patches are being executed in the system. Please try again in a few moments."
	vmraid.db.set_global('__session_status', block and 'stop' or None)
	vmraid.db.set_global('__session_status_message', block and msg or None)
	vmraid.db.commit()

def check_session_stopped():
	if vmraid.db.get_global("__session_status")=='stop':
		vmraid.msgprint(vmraid.db.get_global("__session_status_message"))
		raise vmraid.SessionStopped('Session Stopped')

def log(msg):
	print (msg)
