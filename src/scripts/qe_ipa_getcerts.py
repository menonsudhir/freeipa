#!/usr/bin/python

import dbus
import time

certs = {}
bus = dbus.SystemBus()
obj = bus.get_object('org.fedorahosted.certmonger', '/org/fedorahosted/certmonger')
obj_if = dbus.Interface(obj, 'org.fedorahosted.certmonger')

for certreq in obj_if.get_requests():
    certdata = {}
    req_obj = bus.get_object('org.fedorahosted.certmonger', certreq)
    req_obj_if = dbus.Interface(req_obj, 'org.fedorahosted.certmonger.request')
    req_prop_if = dbus.Interface(req_obj, 'org.freedesktop.DBus.Properties')
    # for certattr in ['nickname', 'cert-nickname', 'status', 'not-valid-after', 'ca-error']:
    #     value = req_prop_if.Get('org.fedorahosted.certmonger.request', certattr)
    #     certdata[certattr] = value
    # certs[certdata['nickname']] = certdata
    certdata['nickname'] = str(req_prop_if.Get('org.fedorahosted.certmonger.request', 'nickname'))
    certdata['status'] = str(req_prop_if.Get('org.fedorahosted.certmonger.request', 'status'))
    certdata['ca-error'] = str(req_prop_if.Get('org.fedorahosted.certmonger.request', 'ca-error'))
    exp1 = req_prop_if.Get('org.fedorahosted.certmonger.request', 'not-valid-after')
    expiration = time.strftime('%s', time.gmtime(exp1))
    certdata['not-valid-after'] = expiration
    nickname = certdata['nickname']
    certs[nickname] = certdata

print(certs)
