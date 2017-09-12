"""
This is a quick test for IPA installation functionality
"""
import time
from ipa_pytests.qe_install import setup_master, setup_replica, setup_client, setup_ca, setup_kra


class TestQuick(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print "\nClass Setup"
        print "MASTER: ", multihost.master.hostname
        print "REPLICA: ", multihost.replica.hostname
        print "CLIENT: ", multihost.client.hostname
        print "DNSFORWARD: ", multihost.config.dns_forwarder

    def test_0001_setup_master(self, multihost):
        """ Test IPA Master installation """
        setup_master(multihost.master)

    def test_0002_setup_replica(self, multihost):
        """ Test IPA Replica Installation """
        setup_replica(multihost.replica, multihost.master)

    def test_0003_setup_client(self, multihost):
        """ Test IPA Client Installation """
        setup_client(multihost.client, multihost.master)

    def test_0004_user(self, multihost):
        """ Add user on master """
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'user-add', '--first=f', '--last=l', 'mytestuser1'],
                               exp_returncode=0,
                               exp_output='mytestuser1')

    def test_0005_user(self, multihost):
        """ Show user from replica """
        time.sleep(30)
        multihost.replica.kinit_as_admin()
        multihost.replica.qerun(['ipa', 'user-show', 'mytestuser1'],
                                exp_returncode=0,
                                exp_output='mytestuser1')

    def test_0006_user(self, multihost):
        """ Show user from client with id command """
        multihost.client.qerun(['id', 'mytestuser1'],
                               exp_returncode=0,
                               exp_output='mytestuser1')

    def test_0007_kra_install(self, multihost):
        """ Install KRA on given master and replica """
        setup_ca(multihost.replica)
        setup_kra(multihost.master)
        setup_kra(multihost.replica)


    def class_teardown(self, multihost):
        """ Teardown for class """
        print "CLASS_TEARDOWN"
        print "MASTER: ", multihost.master.hostname
        print "REPLICA: ", multihost.replica.hostname
        print "CLIENT: ", multihost.client.hostname
        print "DNSFORWARD: ", multihost.config.dns_forwarder
