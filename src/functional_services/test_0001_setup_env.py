"""
Functional Services IPA Environment Install and configuration
"""

import pytest
from ipa_pytests.qe_install import setup_master, setup_replica, setup_client
from ipa_pytests.qe_install import set_resolv_conf_add_server


class TestSetupIpaEnv(object):
    """ FS IPA Env Setup Class """
    def class_setup(self, multihost):
        """ class setup """
        pass

    @pytest.mark.tier1
    def test_0001_setup_master(self, multihost):
        """ Install IPA Master """
        setup_master(multihost.master)

    @pytest.mark.tier1
    def test_0002_setup_replica(self, multihost):
        """ Install IPA Replica """
        setup_replica(multihost.replica, multihost.master)
        set_resolv_conf_add_server(multihost.replica, multihost.master.ip)

    @pytest.mark.tier1
    def test_0003_setup_client(self, multihost):
        """ Install IPA Client """
        setup_client(multihost.client, multihost.master)
        set_resolv_conf_add_server(multihost.client, multihost.replica.ip)

    def class_teardown(self, multihost):
        """ class teardown """
        pass
