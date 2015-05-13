"""
Functional Services IPA Environment Install and configuration
"""

import pytest
from ipa_pytests.qe_install import setup_master, setup_replica, setup_client


class TestSetupIpaEnv(object):
    """ FS IPA Env Setup Class """
    def class_setup(self, multihost):
        """ class setup """
        print "\nClass Setup"
        print "MASTER: ", multihost.master.hostname
        print "REPLICA: ", multihost.replica.hostname
        print "CLIENT: ", multihost.client.hostname
        print "DNSFORWARD: ", multihost.config.dns_forwarder

    @pytest.mark.tier1
    def test_0001_setup_master(self, multihost):
        """ Install IPA Master """
        setup_master(multihost.master)

    @pytest.mark.tier1
    def test_0002_setup_replica(self, multihost):
        """ Install IPA Replica """
        setup_replica(multihost.replica, multihost.master)

    @pytest.mark.tier1
    def test_0003_setup_client(self, multihost):
        """ Install IPA Client """
        setup_client(multihost.client, multihost.master)

    def class_teardown(self, multihost):
        """ class teardown """
        print "CLASS_TEARDOWN"
        print "MASTER: ", multihost.master.hostname
        print "REPLICA: ", multihost.replica.hostname
        print "CLIENT: ", multihost.client.hostname
        print "DNSFORWARD: ", multihost.config.dns_forwarder
