"""
TestCases for miscellaneous master install bugs
- These cases should be configured for master only install
- helps handle simple install bug checks post-install
"""
import pytest
from ipa_pytests.qe_install import setup_master, uninstall_server
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.shared import paths


class TestMasterInstallBugs(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        if multihost.master.transport.file_exists(paths.IPADEFAULTCONF):
            print("IPA Server already installed, skipping installation.")
        else:
            setup_master(multihost.master)

    def test_0001_bz1351276(self, multihost):
        """
        Testcase to verify bz1205264
        """
        ipa_ca_fqdn = 'ipa-ca.' + multihost.master.domain.name
        multihost.master.qerun(['dig', '+short', ipa_ca_fqdn],
                               exp_output=multihost.master.ip)

    def class_teardown(self, multihost):
        """ Full suite teardown """
        uninstall_server(multihost.master)
