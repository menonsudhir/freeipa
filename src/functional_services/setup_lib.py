""" Functional Services Setup Support Functions
This includes functions to help setup:
- IPA Env
- HTTP Service
- LDAP Service
"""

from ipa_pytests.qe_install import setup_master, setup_replica, setup_client
from ipa_pytests.qe_install import set_resolv_conf_add_server


# Class for Test Setup/Teardown #####################################


class TestPrep(object):
    """ Session level setup/teardown class """
    def __init__(self, multihost):
        self.multihost = multihost

    def setup(self):
        """
        Session level setup.
        - Add code here that you want run before all modules in test suite.
        - This should be teardown/cleanup code only, not test code.
        """
        fin = '/tmp/ipa_func_svcs_setup_ipa_env_done'
        if not self.multihost.client.transport.file_exists(fin):
            setup_ipa_env(self.multihost)
            self.multihost.client.put_file_contents(fin, 'x')
        else:
            print("IPA Server Setup has already run.  Skipping")

    def teardown(self):
        """
        Session level teardown
        - Add code here that you want run after all modules in test suite.
        - This should be teardown/cleanup code only, not test code.
        """
        pass

# IPA ###############################################################


def setup_ipa_env(multihost):
    """ Setup IPA Env with Master, Replica, Client """
    _ipa_master(multihost)
    _ipa_replica(multihost)
    _ipa_client(multihost)


def _ipa_master(multihost):
    """ Install IPA Master """
    setup_master(multihost.master)


def _ipa_replica(multihost):
    """ Install IPA Replica """
    setup_replica(multihost.replica, multihost.master)
    set_resolv_conf_add_server(multihost.replica, multihost.master.ip)
    set_resolv_conf_add_server(multihost.master, multihost.replica.ip)


def _ipa_client(multihost):
    """ Install IPA Client """
    setup_client(multihost.client, multihost.master)
    set_resolv_conf_add_server(multihost.client, multihost.replica.ip)
    revip = multihost.client.ip.split('.')[3]
    revnet = multihost.client.ip.split('.')[2] + '.' + \
        multihost.client.ip.split('.')[1] + '.' + \
        multihost.client.ip.split('.')[0] + '.in-addr.arpa.'
    cmd = multihost.client.run_command(['dig', '+short', '-x', multihost.client.ip])
    if multihost.client.hostname not in cmd.stdout_text:
        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa', 'dnsrecord-add', revnet, revip,
                                            '--ptr-rec=%s.' % multihost.client.hostname], raiseonerr=False)
