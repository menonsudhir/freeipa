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
        pass

    def class_teardown(self, multihost):
        """ Class Teardown """
        pass

    @pytest.mark.skip(reason="Skipping due to bz1302127")
    def test_0008_renew_kra_agent_cert(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Renew KRA agent cert

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        pass

    @pytest.mark.skip(reason="Skipping due to bz1302127")
    def test_0009_install_kra_after_ipa_cert_renewed(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Install KRA after IPA cert renewed

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        pass
