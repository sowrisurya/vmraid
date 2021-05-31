from __future__ import unicode_literals
import vmraid

def execute():
    vmraid.reload_doc('core', 'doctype', 'system_settings')
    vmraid.db.sql("update `tabSystem Settings` set allow_error_traceback=1")
