
import vmraid

def execute():
    vmraid.db.sql('''
        DELETE from `tabDocType`
        WHERE name = 'Feedback Request'
    ''')