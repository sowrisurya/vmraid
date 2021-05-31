# -*- coding: utf-8 -*-
# Copyright (c) 2018, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

from collections import Counter
import datetime
import inspect
import json
import re
import time
import vmraid
import sqlparse

from vmraid import _

RECORDER_INTERCEPT_FLAG = "recorder-intercept"
RECORDER_REQUEST_SPARSE_HASH = "recorder-requests-sparse"
RECORDER_REQUEST_HASH = "recorder-requests"


def sql(*args, **kwargs):
	start_time = time.time()
	result = vmraid.db._sql(*args, **kwargs)
	end_time = time.time()

	stack = list(get_current_stack_frames())

	if vmraid.db.db_type == "postgres":
		query = vmraid.db._cursor.query
	else:
		query = vmraid.db._cursor._executed

	query = sqlparse.format(query.strip(), keyword_case="upper", reindent=True)

	# Collect EXPLAIN for executed query
	if query.lower().strip().split()[0] in ("select", "update", "delete"):
		# Only SELECT/UPDATE/DELETE queries can be "EXPLAIN"ed
		explain_result = vmraid.db._sql("EXPLAIN {}".format(query), as_dict=True)
	else:
		explain_result = []

	data = {
		"query": query,
		"stack": stack,
		"explain_result": explain_result,
		"time": start_time,
		"duration": float("{:.3f}".format((end_time - start_time) * 1000)),
	}

	vmraid.local._recorder.register(data)
	return result


def get_current_stack_frames():
	try:
		current = inspect.currentframe()
		frames = inspect.getouterframes(current, context=10)
		for frame, filename, lineno, function, context, index in list(reversed(frames))[:-2]:
			if "/apps/" in filename:
				yield {
					"filename": re.sub(".*/apps/", "", filename),
					"lineno": lineno,
					"function": function,
				}
	except Exception:
		pass

def record():
	if __debug__:
		if vmraid.cache().get_value(RECORDER_INTERCEPT_FLAG):
			vmraid.local._recorder = Recorder()


def dump():
	if __debug__:
		if hasattr(vmraid.local, "_recorder"):
			vmraid.local._recorder.dump()


class Recorder:
	def __init__(self):
		self.uuid = vmraid.generate_hash(length=10)
		self.time = datetime.datetime.now()
		self.calls = []
		self.path = vmraid.request.path
		self.cmd = vmraid.local.form_dict.cmd or ""
		self.method = vmraid.request.method
		self.headers = dict(vmraid.local.request.headers)
		self.form_dict = vmraid.local.form_dict
		_patch()

	def register(self, data):
		self.calls.append(data)

	def dump(self):
		request_data = {
			"uuid": self.uuid,
			"path": self.path,
			"cmd": self.cmd,
			"time": self.time,
			"queries": len(self.calls),
			"time_queries": float(
				"{:0.3f}".format(sum(call["duration"] for call in self.calls))
			),
			"duration": float(
				"{:0.3f}".format((datetime.datetime.now() - self.time).total_seconds() * 1000)
			),
			"method": self.method,
		}
		vmraid.cache().hset(RECORDER_REQUEST_SPARSE_HASH, self.uuid, request_data)
		vmraid.publish_realtime(
			event="recorder-dump-event", message=json.dumps(request_data, default=str)
		)

		self.mark_duplicates()

		request_data["calls"] = self.calls
		request_data["headers"] = self.headers
		request_data["form_dict"] = self.form_dict
		vmraid.cache().hset(RECORDER_REQUEST_HASH, self.uuid, request_data)

	def mark_duplicates(self):
		counts = Counter([call["query"] for call in self.calls])
		for index, call in enumerate(self.calls):
			call["index"] = index
			call["exact_copies"] = counts[call["query"]]


def _patch():
	vmraid.db._sql = vmraid.db.sql
	vmraid.db.sql = sql


def do_not_record(function):
	def wrapper(*args, **kwargs):
		if hasattr(vmraid.local, "_recorder"):
			del vmraid.local._recorder
			vmraid.db.sql = vmraid.db._sql
		return function(*args, **kwargs)

	return wrapper


def administrator_only(function):
	def wrapper(*args, **kwargs):
		if vmraid.session.user != "Administrator":
			vmraid.throw(_("Only Administrator is allowed to use Recorder"))
		return function(*args, **kwargs)

	return wrapper


@vmraid.whitelist()
@do_not_record
@administrator_only
def status(*args, **kwargs):
	return bool(vmraid.cache().get_value(RECORDER_INTERCEPT_FLAG))


@vmraid.whitelist()
@do_not_record
@administrator_only
def start(*args, **kwargs):
	vmraid.cache().set_value(RECORDER_INTERCEPT_FLAG, 1)


@vmraid.whitelist()
@do_not_record
@administrator_only
def stop(*args, **kwargs):
	vmraid.cache().delete_value(RECORDER_INTERCEPT_FLAG)


@vmraid.whitelist()
@do_not_record
@administrator_only
def get(uuid=None, *args, **kwargs):
	if uuid:
		result = vmraid.cache().hget(RECORDER_REQUEST_HASH, uuid)
	else:
		result = list(vmraid.cache().hgetall(RECORDER_REQUEST_SPARSE_HASH).values())
	return result


@vmraid.whitelist()
@do_not_record
@administrator_only
def delete(*args, **kwargs):
	vmraid.cache().delete_value(RECORDER_REQUEST_SPARSE_HASH)
	vmraid.cache().delete_value(RECORDER_REQUEST_HASH)
