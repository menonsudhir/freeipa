"""
Vault Delete tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements

# from .lib import setup_test_prereqs, teardown_test_prereqs
import data  # pylint: disable=relative-import


class TestVaultDelete(object):
    """
    Password Vault Delete Tests
    """
    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'delete')
        multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_priv'])
        multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_user',
                                '--user=' + data.USER1])
        multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_shared',
                                '--shared'])
        multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_service',
                                '--service=' + data.SERVICE1])
        multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_user_vault_fail',
                                '--user=' + data.USER1])
        multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_shared_vault_fail',
                                '--shared'])
        multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_service_vault_fail',
                                '--service=' + data.SERVICE1])

    def class_teardown(self, multihost):
        """ Class Teardown """
        multihost.master.qerun(['ipa', 'vault-del', data.PREFIX + '_user_vault_fail',
                                '--user=' + data.USER1])
        multihost.master.qerun(['ipa', 'vault-del', data.PREFIX + '_shared_vault_fail',
                                '--shared'])
        multihost.master.qerun(['ipa', 'vault-del', data.PREFIX + '_service_vault_fail',
                                '--service=' + data.SERVICE1])

    def test_0001_successfully_delete_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully delete vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-del', data.PREFIX + '_vault_priv']
        multihost.master.qerun(runcmd)

    def test_0002_successfully_delete_shared_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully delete shared vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-del', data.PREFIX + '_vault_shared', '--shared']
        multihost.master.qerun(runcmd)

    def test_0003_successfully_delete_user_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully delete user vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-del', data.PREFIX + '_vault_user', '--user=' + data.USER1]
        multihost.master.qerun(runcmd)

    def test_0004_successfully_delete_service_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully delete service vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-del', data.PREFIX + '_vault_service',
                  '--service=' + data.SERVICE1]
        multihost.master.qerun(runcmd)

    def test_0005_successfully_continue_on_delete_vault_failure(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully continue on delete vault failure

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-del', '--continue', data.PREFIX + '_vault_priv']
        multihost.master.qerun(runcmd, exp_returncode=0, exp_output="Failed to remove")

    def test_0006_fail_to_delete_non_existent_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to delete non_existent vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-del', 'dne_vault']
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0007_fail_to_delete_user_vault_with_shared_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to delete user vault with shared option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-del', data.PREFIX + '_user_vault_fail', '--shared']
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0008_fail_to_delete_service_vault_with_user_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to delete service vault with user option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-del', data.PREFIX + '_service_vault_fail', '--user=' + data.USER1]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0009_fail_to_delete_shared_fault_with_service_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to delete shared fault with service option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-del', data.PREFIX + '_shared_vault_fail',
                  '--service=' + data.SERVICE1]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0010_fail_to_delete_user_vault_with_wrong_user(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to delete user vault with wrong user

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-del', data.PREFIX + '_user_vault_fail', '--user=admin']
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0011_fail_to_delete_user_vault_with_non_existent_user(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to delete user vault with non_existent user

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-del', data.PREFIX + '_user_vault_fail', '--user=dne']
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0012_fail_to_delete_service_vault_with_wrong_service(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to delete service vault with wrong service

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-del', data.PREFIX + '_service_vault_fail',
                  '--service=http/' + multihost.master.hostname]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0013_fail_to_delete_service_vault_with_non_existent_service(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to delete service vault with non_existent service

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-del', data.PREFIX + '_service_vault_fail',
                  '--service=dne/' + multihost.master.hostname]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")
