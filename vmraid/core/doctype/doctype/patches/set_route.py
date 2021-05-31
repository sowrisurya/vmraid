import vmraid
from vmraid.desk.utils import slug

def execute():
    for doctype in vmraid.get_all('DocType', ['name', 'route'], dict(istable=0)):
        if not doctype.route:
            vmraid.db.set_value('DocType', doctype.name, 'route', slug(doctype.name), update_modified = False)