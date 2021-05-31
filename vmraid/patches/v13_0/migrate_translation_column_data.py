import vmraid

def execute():
	vmraid.reload_doctype('Translation')
	vmraid.db.sql("UPDATE `tabTranslation` SET `translated_text`=`target_name`, `source_text`=`source_name`, `contributed`=0")
