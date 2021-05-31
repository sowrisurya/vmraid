import vmraid

def execute():
    for name in ('desktop', 'space'):
        vmraid.delete_doc('Page', name)