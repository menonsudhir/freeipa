"""
Vault Remove-Member tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements

from .lib import setup_test_prereqs, teardown_test_prereqs
import data  # pylint: disable=relative-import


class TestVaultRemoveMember(object):
    """
    Password Vault Remove Member Tests
    """
    def class_setup(self, multihost):
        """
        Setup for TestVaultRemoveMember
        - add users/groups/services and vaults
        """
        data.init(multihost, 'remove_member')
        setup_test_prereqs(multihost, prefix=data.PREFIX)

        for vault in [data.PRIV_VAULT, data.USER_VAULT, data.SHARED_VAULT, data.SERVICE_VAULT]:
            users = '{remove_member_user1,remove_member_user2,remove_member_user3}'
            groups = '{remove_member_group1,remove_member_group2,remove_member_group3}'
            services = '{remove_member_service1/' + multihost.master.hostname + \
                       ',remove_member_service2/' + multihost.master.hostname + \
                       ',remove_member_service3/' + multihost.master.hostname + '}'
            runcmd = ['ipa', 'vault-add-member'] + vault + \
                     ['--users=' + users, '--groups=' + groups, '--services=' + services]
            runcmd = " ".join(runcmd)
            multihost.master.qerun(runcmd)

    def class_teardown(self, multihost):
        """ Class Teardown for TestVaultRemoveMember """
        teardown_test_prereqs(multihost, prefix=data.PREFIX)

    def test_0001_successfully_remove_user_from_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove user from vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-remove-member'] + data.PRIV_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0002_successfully_remove_multiple_users_from_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove multiple users from vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-remove-member'] + data.PRIV_VAULT + \
                 ['--users={' + data.PREFIX + '_user2,' + data.PREFIX + '_user3}']
        # must convert to string because we're using {}'s in command line for multiple options.
        runcmd = " ".join(runcmd)
        multihost.master.qerun(runcmd)

    def test_0003_successfully_remove_group_from_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove group from vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-remove-member'] + data.PRIV_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0004_successfully_remove_multiple_groups_from_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove multiple groups from vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-remove-member'] + data.PRIV_VAULT + \
                 ['--groups={' + data.PREFIX + '_group2,' + data.PREFIX + '_group3}']
        # must convert to string because we're using {}'s in command line for multiple options.
        runcmd = " ".join(runcmd)
        multihost.master.qerun(runcmd)

    def test_0005_successfully_remove_service_from_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove service from vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        service1 = data.PREFIX + '_service1/' + multihost.master.hostname
        runcmd = ['ipa', 'vault-remove-member'] + data.PRIV_VAULT + ['--services=' + service1]
        multihost.master.qerun(runcmd)

    def test_0006_successfully_remove_multiple_services_from_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove multiple services from vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        service2 = data.PREFIX + '_service2/' + multihost.master.hostname
        service3 = data.PREFIX + '_service3/' + multihost.master.hostname
        services = '{' + service2 + ',' + service3 + '}'
        runcmd = ['ipa', 'vault-remove-member'] + data.PRIV_VAULT + ['--services=' + services]
        # must convert to string because we're using {}'s in command line for multiple options.
        runcmd = " ".join(runcmd)
        multihost.master.qerun(runcmd)

    def test_0007_successfully_remove_user_from_shared_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove user from shared vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-remove-member'] + data.SHARED_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0008_successfully_remove_group_from_shared_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove group from shared vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-remove-member'] + data.SHARED_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0009_successfully_remove_service_from_shared_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove service from shared vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        service1 = data.PREFIX + '_service1/' + multihost.master.hostname
        runcmd = ['ipa', 'vault-remove-member'] + data.SHARED_VAULT + ['--services=' + service1]
        multihost.master.qerun(runcmd)

    def test_0010_successfully_remove_user_from_user_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove user from user vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-remove-member'] + data.USER_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0011_successfully_remove_group_from_user_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove group from user vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-remove-member'] + data.USER_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0012_successfully_remove_service_from_user_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove service from user vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        service1 = data.PREFIX + '_service1/' + multihost.master.hostname
        runcmd = ['ipa', 'vault-remove-member'] + data.USER_VAULT + ['--services=' + service1]
        multihost.master.qerun(runcmd)

    def test_0013_successfully_remove_user_from_service_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove user from service vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-remove-member'] + data.SERVICE_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0014_successfully_remove_group_from_service_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove group from service vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-remove-member'] + data.SERVICE_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0015_successfully_remove_service_from_service_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove service from service vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        service1 = data.PREFIX + '_service1/' + multihost.master.hostname
        runcmd = ['ipa', 'vault-remove-member'] + data.SERVICE_VAULT + ['--services=' + service1]
        multihost.master.qerun(runcmd)

    def test_0016_fail_to_remove_user_from_vault_if_already_removed(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove user from vault if already removed

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # This requires earlier test case that removes a user from vault
        runcmd = ['ipa', 'vault-remove-member'] + data.PRIV_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="This entry is not a member")

    def test_0017_fail_to_remove_group_from_vault_if_already_removed(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove group from vault if already removed

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # This requires earlier test case that removes a group from vault
        runcmd = ['ipa', 'vault-remove-member'] + data.PRIV_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="This entry is not a member")

    def test_0018_fail_to_remove_user_from_non_existent_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove user from non_existent vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-remove-member'] + data.DNE_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0019_fail_to_remove_user_from_shared_vault_without_shared_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove user from shared vault without shared option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-remove-member', data.PREFIX + '_vault_shared', '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0020_fail_to_remove_user_from_service_vault_without_service_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove user from service vault without service option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-remove-member', data.PREFIX + '_vault_service', '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0021_fail_to_remove_non_existent_user_from_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove non_existent user from vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-remove-member'] + data.PRIV_VAULT + ['--users=dne']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="not a member")

    def test_0022_fail_to_remove_non_existent_group_from_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove non_existent group from vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-remove-member'] + data.PRIV_VAULT + ['--groups=dne']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="not a member")

    def test_0023_fail_to_remove_user_from_service_vault_with_non_existent_service_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove user from service vault with non_existent service option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        dne_service = "dne/" + multihost.master.hostname
        runcmd = ['ipa', 'vault-remove-member', data.PREFIX + '_vault_service',
                  '--service=' + dne_service, '--users=' + data.PREFIX + '_user2']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0024_fail_to_remove_user_from_user_vault_with_non_existent_user_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove user from user vault with non_existent user option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-remove-member', data.PREFIX + '_vault_user',
                  '--user=dne', '--users=' + data.PREFIX + '_user2']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0025_fail_to_remove_user_from_user_vault_with_wrong_user_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove user from user vault with wrong user option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # This requires that ' + data.PREFIX + '_vault_user is not created with --user=' + data.PREFIX + '_user1
        runcmd = ['ipa', 'vault-remove-member', data.PREFIX + '_vault_user',
                  '--user=' + data.PREFIX + '_user1', '--users=' + data.PREFIX + '_user2']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0026_fail_to_remove_user_from_service_vault_with_wrong_service_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove user from service vault with wrong service option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        wrong_service = data.PREFIX + "_service1/" + multihost.master.hostname
        runcmd = ['ipa', 'vault-remove-member', data.PREFIX + '_vault_service',
                  '--service=' + wrong_service, '--users=' + data.PREFIX + '_user2']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")
