import vmraid

def execute():
    for web_form_name in vmraid.db.get_all('Web Form', pluck='name'):
        web_form = vmraid.get_doc('Web Form', web_form_name)
        doctype_layout = vmraid.get_doc(dict(
            doctype = 'DocType Layout',
            document_type = web_form.doc_type,
            name = web_form.title,
            route = web_form.route,
            fields = [dict(fieldname = d.fieldname, label=d.label) for d in web_form.web_form_fields if d.fieldname]
        )).insert()
        print(doctype_layout.name)