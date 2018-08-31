"""
Vault Show tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements

from .lib import setup_test_prereqs, teardown_test_prereqs
from . import data  # pylint: disable=relative-import

data.SERVICE_VAULT = []


class TestVaultShow(object):
    """
    Password Vault Show Tests
    """
    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'show')
        setup_test_prereqs(multihost, prefix=data.PREFIX)

    def class_teardown(self, multihost):
        """ Class Teardown """
        teardown_test_prereqs(multihost, prefix=data.PREFIX)

    def test_0001_successfully_show_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully show vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-show'] + data.PRIV_VAULT
        multihost.master.qerun(runcmd)

    def test_0002_successfully_show_user_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully show user vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-show'] + data.USER_VAULT
        multihost.master.qerun(runcmd)

    def test_0003_successfully_show_shared_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully show shared vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-show'] + data.SHARED_VAULT
        multihost.master.qerun(runcmd)

    def test_0004_successfully_show_service_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully show service vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-show'] + data.SERVICE_VAULT
        multihost.master.qerun(runcmd)

    def test_0005_fail_to_show_non_existent_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to show non_existent vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-show'] + data.DNE_VAULT
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0006_fail_to_show_user_vault_with_service_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to show user vault with service option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-show', data.PREFIX + '_vault_user',
                  '--service=' + data.SERVICE1]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0007_fail_to_show_shared_vault_with_user_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to show shared vault with user option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-show', data.PREFIX + '_vault_shared', '--user=' + data.USER1]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0008_fail_to_show_service_vault_with_shared_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to show service vault with shared option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-show', data.PREFIX + '_vault_service', '--shared']
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0009_fail_to_show_user_vault_with_non_existent_user_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to show user vault with non_existent user option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-show', data.PREFIX + '_vault_user', '--user=dne']
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0010_fail_to_show_service_vault_with_non_existent_service_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to show service vault with non_existent service option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-show', data.PREFIX + '_vault_service',
                  '--service=dne/' + multihost.master.hostname]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")
