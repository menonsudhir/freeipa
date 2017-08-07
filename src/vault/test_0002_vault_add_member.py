"""
Vault Add-Member tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements

from .lib import setup_test_prereqs, teardown_test_prereqs
import data  # pylint: disable=relative-import


class TestVaultAddMember(object):
    """
    Password Vault Add Member Tests
    """
    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'add_member')
        setup_test_prereqs(multihost, prefix=data.PREFIX)

    def class_teardown(self, multihost):
        """ Class Teardown """
        teardown_test_prereqs(multihost, prefix=data.PREFIX)

    def test_0001_successfully_add_user_to_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add user to vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-member'] + data.PRIV_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0002_successfully_add_multiple_users_to_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add multiple users to vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-member'] + data.PRIV_VAULT + \
                 ['--users={' + data.PREFIX + '_user2,' + data.PREFIX + '_user3}']
        # must convert to string because we're using {}'s in command line for multiple options.
        runcmd = " ".join(runcmd)
        multihost.master.qerun(runcmd)

    def test_0003_successfully_add_group_to_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add group to vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-member'] + data.PRIV_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0004_successfully_add_multiple_groups_to_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add multiple groups to vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-member'] + data.PRIV_VAULT + \
                 ['--groups={' + data.PREFIX + '_group2,' + data.PREFIX + '_group3}']
        # must convert to string because we're using {}'s in command line for multiple options.
        runcmd = " ".join(runcmd)
        multihost.master.qerun(runcmd)

    def test_0005_successfully_add_service_to_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add service to vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        service1 = data.PREFIX + '_service1/' + multihost.master.hostname
        runcmd = ['ipa', 'vault-add-member'] + data.PRIV_VAULT + ['--services=' + service1]
        multihost.master.qerun(runcmd)

    def test_0006_successfully_add_multiple_services_to_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add multiple services to vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        service2 = data.PREFIX + '_service2/' + multihost.master.hostname
        service3 = data.PREFIX + '_service3/' + multihost.master.hostname
        services = '{' + service2 + ',' + service3 + '}'
        runcmd = ['ipa', 'vault-add-member'] + data.PRIV_VAULT + ['--services=' + services]
        # must convert to string because we're using {}'s in command line for multiple options.
        runcmd = " ".join(runcmd)
        multihost.master.qerun(runcmd)

    def test_0007_successfully_add_user_to_shared_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add user to shared vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-member'] + data.SHARED_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0008_successfully_add_group_to_shared_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add group to shared vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-member'] + data.SHARED_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0009_successfully_add_service_to_shared_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add service to shared vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        service1 = data.PREFIX + '_service1/' + multihost.master.hostname
        runcmd = ['ipa', 'vault-add-member'] + data.SHARED_VAULT + ['--services=' + service1]
        multihost.master.qerun(runcmd)

    def test_0010_successfully_add_user_to_user_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add user to user vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-member'] + data.USER_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0011_successfully_add_group_to_user_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add group to user vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-member'] + data.USER_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0012_successfully_add_service_to_user_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add service to user vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        service1 = data.PREFIX + '_service1/' + multihost.master.hostname
        runcmd = ['ipa', 'vault-add-member'] + data.USER_VAULT + ['--services=' + service1]
        multihost.master.qerun(runcmd)

    def test_0013_successfully_add_user_to_service_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add user to service vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-member'] + data.SERVICE_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0014_successfully_add_group_to_service_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add group to service vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-member'] + data.SERVICE_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0015_successfully_add_service_to_service_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add service to service vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        service1 = data.PREFIX + '_service1/' + multihost.master.hostname
        runcmd = ['ipa', 'vault-add-member'] + data.SERVICE_VAULT + ['--services=' + service1]
        multihost.master.qerun(runcmd)

    def test_0016_fail_to_add_user_with_same_name_to_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add user with same name to vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # This requires earlier test case that adds user to vault
        runcmd = ['ipa', 'vault-add-member'] + data.PRIV_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="This entry is already a member")

    def test_0017_fail_to_add_group_with_same_name_to_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add group with same name to vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # This requires earlier test case that adds group to vault
        runcmd = ['ipa', 'vault-add-member'] + data.PRIV_VAULT + ['--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="This entry is already a member")

    def test_0018_fail_to_add_service_with_same_name_to_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add service with same name to vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # This requires earlier test case that adds service to vault
        service1 = data.PREFIX + '_service1/' + multihost.master.hostname
        runcmd = ['ipa', 'vault-add-member'] + data.PRIV_VAULT + ['--services=' + service1]
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="This entry is already a member")

    def test_0019_fail_to_add_user_to_non_existent_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add user to non_existent vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-member'] + data.DNE_VAULT + ['--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0020_fail_to_add_user_to_shared_vault_without_shared_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add user to shared vault without shared option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-member', data.PREFIX + '_vault_shared', '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0021_fail_to_add_user_to_service_vault_without_service_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add user to shared vault without service option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-member', data.PREFIX + '_vault_service', '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0022_fail_to_add_non_existent_user_to_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add non_existent user to vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-member'] + data.PRIV_VAULT + ['--users=dne']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="no such entry")

    def test_0023_fail_to_add_non_existent_group_to_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add non_existent group to vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add-member'] + data.PRIV_VAULT + ['--groups=dne']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="no such entry")

    def test_0024_fail_to_add_user_to_service_vault_for_non_existent_service(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add user to service vault for non_existent service

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        dne_service = "dne/" + multihost.master.hostname
        runcmd = ['ipa', 'vault-add-member', data.PREFIX + '_vault_service',
                  '--service=' + dne_service, '--users=' + data.PREFIX + '_user2']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0025_fail_to_add_user_to_user_vault_for_wrong_user(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add user to user vault for wrong user

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # This requires that member_vault_user is not created with --user=member_user1
        runcmd = ['ipa', 'vault-add-member', data.PREFIX + '_vault_user',
                  '--user=' + data.PREFIX + '_user1', '--users=' + data.PREFIX + '_user2']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")

    def test_0026_fail_to_add_user_to_service_vault_for_wrong_service(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add user to service vault for wrong service

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        wrong_service = "member_service1/" + multihost.master.hostname
        runcmd = ['ipa', 'vault-add-member', data.PREFIX + '_vault_service',
                  '--service=' + wrong_service, '--users=' + data.PREFIX + '_user2']
        multihost.master.qerun(runcmd, exp_returncode=2,
                               exp_output="vault not found")
