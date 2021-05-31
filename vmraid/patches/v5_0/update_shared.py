from __future__ import unicode_literals
import vmraid
import vmraid.share

def execute():
	vmraid.reload_doc("core", "doctype", "docperm")
	vmraid.reload_doc("core", "doctype", "docshare")
	vmraid.reload_doc('email', 'doctype', 'email_account')

	# default share to all writes
	vmraid.db.sql("""update tabDocPerm set `share`=1 where ifnull(`write`,0)=1 and ifnull(`permlevel`,0)=0""")

	# every user must have access to his / her own detail
	users = vmraid.get_all("User", filters={"user_type": "System User"})
	usernames = [user.name for user in users]
	for user in usernames:
		vmraid.share.add("User", user, user, write=1, share=1)

	# move event user to shared
	if vmraid.db.exists("DocType", "Event User"):
		for event in vmraid.get_all("Event User", fields=["parent", "person"]):
			if event.person in usernames:
				if not vmraid.db.exists("Event", event.parent):
					vmraid.db.sql("delete from `tabEvent User` where parent = %s",event.parent)
				else:
					vmraid.share.add("Event", event.parent, event.person, write=1)

		vmraid.delete_doc("DocType", "Event User")

	# move note user to shared
	if vmraid.db.exists("DocType", "Note User"):
		for note in vmraid.get_all("Note User", fields=["parent", "user", "permission"]):
			perm = {"read": 1} if note.permission=="Read" else {"write": 1}
			if note.user in usernames:
				vmraid.share.add("Note", note.parent, note.user, **perm)

		vmraid.delete_doc("DocType", "Note User")
