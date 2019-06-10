""" Functional Services Setup Support Functions
This includes functions to help setup:
- IPA Env
- HTTP Service
- LDAP Service
"""

import netaddr
from ipa_pytests.qe_install import setup_master, setup_replica, setup_client
from ipa_pytests.qe_install import set_resolv_conf_add_server
from ipa_pytests.shared.utils import get_revnet_info


def ipa_master(multihost):
    """ Install IPA Master """
    setup_master(multihost.master)


def ipa_replica(multihost):
    """ Install IPA Replica """
    setup_replica(multihost.replica, multihost.master)
    set_resolv_conf_add_server(multihost.replica, multihost.master.ip)
    set_resolv_conf_add_server(multihost.master, multihost.replica.ip)


def ipa_client(multihost):
    """ Install IPA Client """
    setup_client(multihost.client, multihost.master, module_stream='client')
    set_resolv_conf_add_server(multihost.client, multihost.replica.ip)
    revip, revnet = get_revnet_info(multihost.client.ip)
    run = ['dig', '+short', '-x', multihost.client.ip]
    cmd = multihost.client.run_command(run)
    hname = multihost.client.hostname
    if multihost.client.hostname not in cmd.stdout_text:
        multihost.master.kinit_as_admin()
        run = ['ipa', 'dnsrecord-add', revnet, revip,
               '--ptr-rec={}.'.format(hname)]
        cmd = multihost.master.run_command(run,
                                           raiseonerr=False)
