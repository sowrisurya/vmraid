import vmraid
from vmraid import msgprint, throw, _


# ruleid: vmraid-missing-translate-function
throw("Error Occured")

# ruleid: vmraid-missing-translate-function
vmraid.throw("Error Occured")

# ruleid: vmraid-missing-translate-function
vmraid.msgprint("Useful message")

# ruleid: vmraid-missing-translate-function
msgprint("Useful message")


# ok: vmraid-missing-translate-function
translatedmessage = _("Hello")

# ok: vmraid-missing-translate-function
throw(translatedmessage)

# ok: vmraid-missing-translate-function
msgprint(translatedmessage)

# ok: vmraid-missing-translate-function
msgprint(_("Helpful message"))

# ok: vmraid-missing-translate-function
vmraid.throw(_("Error occured"))
