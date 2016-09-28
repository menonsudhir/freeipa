"""
Vault KRA Install tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements

import pytest
from ipa_pytests.shared.utils import get_domain_level


class TestVaultKRAInstall(object):
    """
    Password Vault KRA Install Tests
    tests require uninstall to work.  this is blocked by bug:
    https://bugzilla.redhat.com/show_bug.cgi?id=1302127
    """

    def class_setup(self, multihost):
        """ Class Setup """
        runcmd = ['ipa-kra-install', '--uninstall']
        multihost.master.run_command(runcmd, raiseonerr=False)

    def class_teardown(self, multihost):
        """ Class Teardown """
        pass

    @pytest.mark.skip(reason="Skipping due to bz1302127")
    def test_0001_successfully_install_kra_on_master(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully install KRA on Master
        """
        runcmd = ['ipa-kra-install', '-p', multihost.master.config.dirman_pw, '-U']
        multihost.master.qerun(runcmd)

    @pytest.mark.skip(reason="Skipping due to bz1302127")
    def test_0002_successfully_uninstall_kra_from_master(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully uninstall KRA from master
        """
        runcmd = ['ipa-kra-install', '--uninstall']
        multihost.master.qerun(runcmd)

    @pytest.mark.skip(reason="Skipping due to bz1302127")
    def test_0003_successfully_install_first_kra_on_replica(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully install first KRA on Replica
        """
        runcmd = ['ipa-kra-install', '-p', multihost.replica.config.dirman_pw, '-U']
        multihost.replica.qerun(runcmd)

    @pytest.mark.skip(reason="Skipping due to bz1302127")
    def test_0004_successfully_uninstall_kra_from_replica(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully uninstall first KRA from replica
        """
        runcmd = ['ipa-kra-install', '--uninstall']
        multihost.replica.qerun(runcmd)

    @pytest.mark.skip(reason="Skipping due to bz1302127")
    def test_0005_successfully_install_second_kra_on_replica(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully install second KRA on Replica
        """
        runcmd = ['ipa-kra-install', '-p', multihost.master.config.dirman_pw, '-U']
        multihost.master.qerun(runcmd)
        domain_level = get_domain_level(multihost.master)
        if domain_level == 0:
            replica_file = '/var/lib/ipa/replica-info-' + multihost.replica.hostname + '.gpg'
            runcmd.append(replica_file)
        multihost.replica.qerun(runcmd)

    @pytest.mark.skip(reason="Skipping due to bz1302127")
    def test_0006_successfully_install_second_kra_on_master(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully install second KRA on Master
        """

    @pytest.mark.skip(reason="Skipping due to bz1302127")
    def test_0007_fail_to_install_on_replica_without_replica_file(self, multihost):
        """
        IDM-IPA-TC: Vault: Fail to install on Replica without replica file
        """

    @pytest.mark.skip(reason="Skipping due to bz1302127")
    def test_0008_renew_kra_agent_cert(self, multihost):
        """
        IDM-IPA-TC: Vault: Renew KRA agent cert
        """

    @pytest.mark.skip(reason="Skipping due to bz1302127")
    def test_0009_install_kra_after_ipa_cert_renewed(self, multihost):
        """
        IDM-IPA-TC: Vault: Install KRA after IPA cert renewed
        """
