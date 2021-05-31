import vmraid

def execute():
    '''
    Deprecate Feedback Trigger and Rating. This feature was not customizable.
    Now can be achieved via custom Web Forms
    '''
    vmraid.delete_doc('DocType', 'Feedback Trigger')
    vmraid.delete_doc('DocType', 'Feedback Rating')
