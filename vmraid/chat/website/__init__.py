from __future__ import unicode_literals
import vmraid
from   vmraid.chat.util import filter_dict, safe_json_loads

from   vmraid.sessions  import get_geo_ip_country

@vmraid.whitelist(allow_guest = True)
def settings(fields = None):
    fields    = safe_json_loads(fields)

    dsettings = vmraid.get_single('Website Settings')
    response  = dict(
        socketio         = dict(
            port         = vmraid.conf.socketio_port
        ),
        enable           = bool(dsettings.chat_enable),
        enable_from      = dsettings.chat_enable_from,
        enable_to        = dsettings.chat_enable_to,
        room_name        = dsettings.chat_room_name,
        welcome_message  = dsettings.chat_welcome_message,
        operators        = [
            duser.user for duser in dsettings.chat_operators
        ]
    )

    if fields:
        response = filter_dict(response, fields)

    return response

@vmraid.whitelist(allow_guest = True)
def token():
    dtoken             = vmraid.new_doc('Chat Token')

    dtoken.token       = vmraid.generate_hash()
    dtoken.ip_address  = vmraid.local.request_ip
    country            = get_geo_ip_country(dtoken.ip_address)
    if country:
        dtoken.country = country['iso_code']
    dtoken.save(ignore_permissions = True)

    return dtoken.token