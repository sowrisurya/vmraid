from __future__ import unicode_literals

import vmraid

def execute():
    vmraid.reload_doctype('Letter Head')

    # source of all existing letter heads must be HTML
    vmraid.db.sql("update `tabLetter Head` set source = 'HTML'")
