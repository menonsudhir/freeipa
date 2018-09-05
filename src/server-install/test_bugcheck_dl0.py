"""
Overview:
IPA Master install to verify disabling domain level 0 in RHEL 8.0
#1613879
"""

import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_install import uninstall_server
from ipa_pytests.qe_class import qe_use_class_setup
import os


class TestBugCheck(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        os.environ['DOMAIN_LEVEL'] = '0'
        print(os.environ['DOMAIN_LEVEL'])
        print("Master: ", multihost.master.hostname)
        print(" %s is installed on domain-level 0 " % multihost.master.hostname)
        print("Checking ipa server is running on MASTER ")
        ipactl_check = multihost.master.run_command('ipactl status | grep RUNNING', raiseonerr=False)
        if ipactl_check.returncode != 0:
            print("IPA server service not RUNNING.")
        else:
            print("IPA service is running, need to uninstall")
            uninstall_server(multihost.master)

    def test_0001_bz_1613879(self, multihost):
        """
        IDM-IPA-TC : Master-Install : Verify master install with doamin 0
        """
        # using domain level 0 to setup ipa master
        exp_output = "ipa-server-install: error: option domain-level: Domain Level cannot be lower than 1"
        multihost.master.qerun(['ipa-server-install', '-U',
                                '--setup-dns', '--auto-forwarder',
                                '--domain', multihost.master.domain.name,
                                '--realm', multihost.master.domain.realm,
                                '--admin-password', 'SECRET123',
                                '--ds-password', 'SECRET123',
                                '--no-reverse', '--domain-level=0'],
                               exp_returncode=2,
                               exp_output=exp_output)

    def class_teardown(self, multihost):
        """ Full suite teardown """
        pass
