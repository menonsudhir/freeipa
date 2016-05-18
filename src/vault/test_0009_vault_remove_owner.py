"""
Vault Remove-Owner tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements

from .lib import setup_test_prereqs, teardown_test_prereqs
import data  # pylint: disable=relative-import


class TestVaultRemoveOwner(object):
    """
    Password Vault Remove Owner Tests
    """
    def class_setup(self, multihost):
        """
        Setup for TestVaultRemoveOwner
        - add users/groups/services and vaults
        """
        data.init(multihost, 'remove_owner')
        setup_test_prereqs(multihost, prefix=data.PREFIX)

        for vault in [data.PRIV_VAULT, data.USER_VAULT, data.SHARED_VAULT, data.SERVICE_VAULT]:
            users = '{' + data.PREFIX + '_user1,' + data.PREFIX + '_user2,' + data.PREFIX + '_user3}'
            groups = '{' + data.PREFIX + '_group1,' + data.PREFIX + '_group2,' + data.PREFIX + '_group3}'
            services = '{' + data.PREFIX + '_service1/' + multihost.master.hostname + \
                       ',' + data.PREFIX + '_service2/' + multihost.master.hostname + \
                       ',' + data.PREFIX + '_service3/' + multihost.master.hostname + '}'

            runcmd = ['ipa', 'vault-add-owner'] + vault + \
                     ['--users=' + users, '--groups=' + groups, '--services=' + services]

            runcmd = " ".join(runcmd)

            multihost.master.qerun(runcmd)

    def class_teardown(self, multihost):
        """ Class Teardown for TestVaultRemoveOwner """
        teardown_test_prereqs(multihost, prefix=data.PREFIX)

    def test_0001_successfully_remove_user_as_owner_from_vault(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully remove user as owner from vault
        """
        runcmd = ['ipa', 'vault-remove-owner'] + data.PRIV_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0002_successfully_remove_multiple_users_as_owner_from_vault(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully remove multiple users as owner from vault
        """
        runcmd = ['ipa', 'vault-remove-owner'] + data.PRIV_VAULT + \
                 ['--users={' + data.PREFIX + '_user2,' + data.PREFIX + '_user3}']
        # must convert to string because we're using {}'s in command line for multiple options.
        runcmd = " ".join(runcmd)
        multihost.master.qerun(runcmd)

    def test_0003_successfully_remove_group_as_owner_from_vault(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully remove group as owner from vault
        """
        runcmd = ['ipa', 'vault-remove-owner'] + data.PRIV_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0004_successfully_remove_multiple_groups_as_owner_from_vault(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully remove multiple groups as owner from vault
        """
        runcmd = ['ipa', 'vault-remove-owner'] + data.PRIV_VAULT + \
                 ['--groups={' + data.PREFIX + '_group2,' + data.PREFIX + '_group3}']
        # must convert to string because we're using {}'s in command line for multiple options.
        runcmd = " ".join(runcmd)
        multihost.master.qerun(runcmd)

    def test_0005_successfully_remove_user_as_owner_from_shared_vault(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully remove user as owner from shared vault
        """
        runcmd = ['ipa', 'vault-remove-owner'] + data.SHARED_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0006_successfully_remove_group_as_owner_from_shared_vault(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully remove group as owner from shared vault
        """
        runcmd = ['ipa', 'vault-remove-owner'] + data.SHARED_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0007_successfully_remove_user_as_owner_from_user_vault(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully remove user as owner from user vault
        """
        runcmd = ['ipa', 'vault-remove-owner'] + data.USER_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0008_successfully_remove_group_as_owner_from_user_vault(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully remove group as owner from user vault
        """
        runcmd = ['ipa', 'vault-remove-owner'] + data.USER_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0009_successfully_remove_user_as_owner_from_service_vault(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully remove user as owner from service vault
        """
        runcmd = ['ipa', 'vault-remove-owner'] + data.SERVICE_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0010_successfully_remove_group_as_owner_from_service_vault(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully remove group as owner from service vault
        """
        runcmd = ['ipa', 'vault-remove-owner'] + data.SERVICE_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0011_fail_to_remove_user_as_owner_from_vault_if_already_removed(self, multihost):
        """
        IDM-IPA-TC: Vault: Fail to remove user as owner from vault if already removed
        """
        # This requires earlier test case that removes user from vault
        runcmd = ['ipa', 'vault-remove-owner'] + data.PRIV_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="This entry is not a member")

    def test_0012_fail_to_remove_group_as_owner_from_vault_if_already_removed(self, multihost):
        """
        IDM-IPA-TC: Vault: Fail to remove group as owner from vault if already removed
        """
        # This requires earlier test case that removes group from vault
        runcmd = ['ipa', 'vault-remove-owner'] + data.PRIV_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="This entry is not a member")

    def test_0013_fail_to_remove_user_as_owner_from_non_existent_vault(self, multihost):
        """
        IDM-IPA-TC: Vault: Fail to remove user as owner from non_existent vault
        """
        runcmd = ['ipa', 'vault-remove-owner'] + data.DNE_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0014_fail_to_remove_user_as_owner_from_shared_vault_without_shared_option(self, multihost):
        """
        IDM-IPA-TC: Vault: Fail to remove user as owner from shared vault without shared option
        """
        runcmd = ['ipa', 'vault-remove-owner', data.PREFIX + '_vault_shared',
                  '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0015_fail_to_remove_user_as_owner_from_service_vault_without_service_option(self, multihost):
        """
        IDM-IPA-TC: Vault: Fail to remove user as owner from service vault without service option
        """
        runcmd = ['ipa', 'vault-remove-owner', data.PREFIX + '_vault_service',
                  '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0016_fail_to_remove_non_existent_user_as_owner_from_vault(self, multihost):
        """
        IDM-IPA-TC: Vault: Fail to remove non_existent user as owner from vault
        """
        runcmd = ['ipa', 'vault-remove-owner'] + data.PRIV_VAULT + ['--users=dne']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="not a member")

    def test_0017_fail_to_remove_non_existent_group_as_owner_from_vault(self, multihost):
        """
        IDM-IPA-TC: Vault: Fail to remove non_existent group as owner from vault
        """
        runcmd = ['ipa', 'vault-remove-owner'] + data.PRIV_VAULT + ['--groups=dne']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="not a member")

    def test_0018_fail_to_remove_user_as_owner_from_service_vault_with_non_existent_service_option(self, multihost):
        """
        IDM-IPA-TC: Vault: Fail to remove user as owner from service vault with non_existent service option
        """
        dne_service = "dne/" + multihost.master.hostname
        runcmd = ['ipa', 'vault-remove-owner', data.PREFIX + '_vault_service',
                  '--service=' + dne_service, '--users=' + data.PREFIX + '_user2']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0019_fail_to_remove_user_as_owner_from_user_vault_with_non_existent_user_option(self, multihost):
        """
        IDM-IPA-TC: Vault: Fail to remove user as owner from user vault with non_existent user option
        """
        dne_service = "dne/" + multihost.master.hostname
        runcmd = ['ipa', 'vault-remove-owner', data.PREFIX + '_vault_user',
                  '--service=' + dne_service, '--users=' + data.PREFIX + '_user2']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0020_fail_to_remove_user_as_owner_from_user_vault_with_wrong_user_option(self, multihost):
        """
        IDM-IPA-TC: Vault: Fail to remove user as owner from user vault with wrong user option
        """
        runcmd = ['ipa', 'vault-remove-owner', data.PREFIX + '_vault_user',
                  '--user=' + data.PREFIX + '_user1', '--users=' + data.PREFIX + '_user2']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0021_fail_to_remove_user_as_owner_from_service_vault_with_wrong_service_option(self, multihost):
        """
        IDM-IPA-TC: Vault: Fail to remove user as owner from service vault with wrong service option
        """
        wrong_service = data.PREFIX + '_service1/' + multihost.master.hostname
        runcmd = ['ipa', 'vault-remove-owner', data.PREFIX + '_vault_service',
                  '--service=' + wrong_service, '--users=' + data.PREFIX + '_user2']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")
