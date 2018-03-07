"""
Overview:
Test to verify #1204504-[RFE] Add access control
so hosts can create their own services
SetUp Requirements:
IPA Server configured on RHEL7.2
IPA Client configured on RHEL7.2
"""

import pytest


class Test_bz_1204504(object):

    """ Test Class for service add """
    def class_setup(self, multihost):
        """ Setup for class """
        print "\nClass Setup"
        print "MASTER: ", multihost.master.hostname
        print "CLIENT: ", multihost.client.hostname

    def test_0001_ipaserviceaddclient(self, multihost):
        """
        IDM-IPA-TC : ipa service-add : ipa service-add adds the corresponding service for client
        """
        multihost.client.run_command(['kdestroy', '-A'])
        multihost.client.run_command(['kinit', '-kt', '/etc/krb5.keytab'])
        multihost.client.run_command(['klist'])
        client_name = multihost.client.hostname
        # Add service to Client
        multihost.client.qerun(['ipa', 'service-add', 'EXAMPLE/' + client_name],
                               exp_returncode=0, exp_output="Added service")

    def test_002_ipaserviceaddmaster(self, multihost):
        """
        IDM-IPA-TC : ipa service-add : ipa service-add adds the corresponding service for master
        """
        master_name = multihost.master.hostname
        multihost.client.run_command(['kinit', '-kt', '/etc/krb5.keytab'])
        # Add service to Master
        multihost.client.qerun(['ipa', 'service-add', 'TEST/' + master_name],
                               exp_returncode=1, exp_output="Insufficient")
