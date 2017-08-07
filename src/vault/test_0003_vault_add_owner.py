"""
Vault Add-Owner tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements

from .lib import setup_test_prereqs, teardown_test_prereqs
import data  # pylint: disable=relative-import


class TestVaultAddOwner(object):
    """
    Password Vault Add Owner Tests
    """
    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'add_owner')
        setup_test_prereqs(multihost, prefix=data.PREFIX)

    def class_teardown(self, multihost):
        """ Class Teardown """
        teardown_test_prereqs(multihost, prefix=data.PREFIX)

    def test_0001_successfully_add_user_as_owner_for_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add user as owner for vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner'] + data.PRIV_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0002_successfully_add_multiple_users_as_owner_for_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add multiple users as owner for vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner'] + data.PRIV_VAULT + \
                 ['--users={' + data.PREFIX + '_user2,' + data.PREFIX + '_user3}']
        # must convert to string because we're using {}'s in command line for multiple options.
        runcmd = " ".join(runcmd)
        multihost.master.qerun(runcmd)

    def test_0003_successfully_add_group_as_owner_for_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add group as owner for vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner'] + data.PRIV_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0004_successfully_add_multiple_groups_as_owner_for_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add multiple groups as owner for vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner'] + data.PRIV_VAULT + \
                 ['--groups={' + data.PREFIX + '_group2,' + data.PREFIX + '_group3}']
        # must convert to string because we're using {}'s in command line for multiple options.
        runcmd = " ".join(runcmd)
        multihost.master.qerun(runcmd)

    def test_0005_successfully_add_user_as_owner_for_shared_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add user as owner for shared vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner'] + data.SHARED_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0006_successfully_add_group_as_owner_for_shared_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add group as owner for shared vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner'] + data.SHARED_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0007_successfully_add_user_as_owner_for_user_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add user as owner for user vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner'] + data.USER_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0008_successfully_add_group_as_owner_for_user_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add group as owner for user vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner'] + data.USER_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0009_successfully_add_user_as_owner_for_service_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add user as owner for service vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner'] + data.SERVICE_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0010_successfully_add_group_as_owner_for_service_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add group as owner for service vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner'] + data.SERVICE_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0011_fail_to_add_same_user_as_owner_for_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add same user as owner for vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # This requires earlier test case that adds user to vault
        runcmd = ['ipa', 'vault-add-owner'] + data.PRIV_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="This entry is already a member")

    def test_0012_fail_to_add_same_group_as_owner_for_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add same group as owner for vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # This requires earlier test case that adds user to vault
        runcmd = ['ipa', 'vault-add-owner'] + data.PRIV_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="This entry is already a member")

    def test_0013_fail_to_add_user_as_owner_to_non_existent_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add user as owner to non_existent vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner'] + data.DNE_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0014_fail_to_add_user_as_owner_to_shared_vault_without_shared_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add user as owner to shared vault without shared option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner', data.PREFIX + '_vault_shared', '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0015_fail_to_add_user_as_owner_to_service_vault_without_service_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add user as owner to service vault without service option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner', data.PREFIX + '_vault_service', '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0016_fail_to_add_non_existent_user_as_owner_to_user_vault_without_user_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add non_existent user as owner to user vault without user option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner', data.PREFIX + '_vault_user', '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0017_fail_to_add_non_existent_user_as_owner_to_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add non_existent user as owner to vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner'] + data.PRIV_VAULT + ['--users=dne']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="no such entry")

    def test_0018_fail_to_add_non_existent_group_as_owner_to_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add non_existent group as owner to vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner'] + data.PRIV_VAULT + ['--groups=dne']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="no such entry")

    def test_0019_fail_to_add_user_as_owner_for_user_vault_with_wrong_user(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add user as owner for user vault with wrong user

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-owner', data.PREFIX + '_vault_user',
                  '--user=' + data.PREFIX + '_user1', '--users=' + data.PREFIX + '_user2']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0020_fail_to_add_user_as_owner_for_service_vault_with_non_existent_service(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add user as owner for service vault with non_existent service

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        dne_service = "dne/" + multihost.master.hostname
        runcmd = ['ipa', 'vault-add-owner', data.PREFIX + '_vault_service',
                  '--service=' + dne_service, '--users=' + data.PREFIX + '_user2']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0021_fail_to_add_user_as_owner_for_service_vault_with_wrong_service(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add user as owner for service vault with wrong service

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        wrong_service = data.PREFIX + '_service1/' + multihost.master.hostname
        runcmd = ['ipa', 'vault-add-owner', data.PREFIX + '_vault_service',
                  '--service=' + wrong_service, '--users=' + data.PREFIX + '_user2']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")
