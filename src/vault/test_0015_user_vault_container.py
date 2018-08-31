"""
User Vault Container tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements

from .lib import setup_test_prereqs, teardown_test_prereqs
from . import data  # pylint: disable=relative-import

CONTAINER_1 = []
CONTAINER_2 = []
CONTAINER_DNE_INVALID_USER = []
CONTAINER_DNE_VALID_USER = []


class TestUserVaultContainerAddOwner(object):
    """
    User Vault Container Add Owner Tests
    """

    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'user_container_add')
        setup_test_prereqs(multihost, prefix=data.PREFIX)

        global CONTAINER_1
        global CONTAINER_DNE_INVALID_USER

        CONTAINER_1 = '--user=testuser1'
        CONTAINER_DNE_INVALID_USER = '--user=dne'

    def class_teardown(self, multihost):
        """ Class Teardown """
        teardown_test_prereqs(multihost, prefix=data.PREFIX)

    def test_0001_successfully_add_container_owner_user_to_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add container owner user to user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1,
                  '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0002_successfully_add_container_owner_group_to_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add container owner group to user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1,
                  '--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0003_successfully_add_container_owner_service_to_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add container owner service to user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1,
                  '--services=' + data.PREFIX + '_service1/' + multihost.master.hostname]
        multihost.master.qerun(runcmd)

    def test_0004_fail_to_add_container_owner_non_existent_user_to_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add container owner non_existent user to user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1, '--users=dne']
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="no such entry")

    def test_0005_fail_to_add_container_owner_non_existent_group_to_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add container owner non_existent group to user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1, '--groups=dne']
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="no such entry")

    def test_0006_fail_to_add_container_owner_non_existent_service_to_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add container owner non_existent service to user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1,
                  '--services=dne/' + multihost.master.hostname]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="no such entry")

    def test_0007_fail_to_add_container_owner_user_to_non_existent_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add container owner user to non_existent user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_DNE_INVALID_USER,
                  '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="not found")

    def test_0008_fail_to_add_container_owner_group_to_non_existent_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add container owner group to non_existent user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_DNE_INVALID_USER,
                  '--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="not found")

    def test_0009_fail_to_add_container_owner_service_to_non_existent_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add container owner service to non_existent user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_DNE_INVALID_USER,
                  '--services=' + data.PREFIX + '_service1/' + multihost.master.hostname]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="not found")


class TestUserVaultContainerRemoveOwner(object):
    """
    User Vault Container Remove Owner Tests
    """

    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'user_container_remove')
        setup_test_prereqs(multihost, prefix=data.PREFIX)

        global CONTAINER_1
        global CONTAINER_DNE_INVALID_USER
        CONTAINER_1 = '--user=testuser1'
        CONTAINER_DNE_INVALID_USER = '--user=dne'

        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1,
                  '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1,
                  '--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1,
                  '--services=' + data.PREFIX + '_service1/' + multihost.master.hostname]
        multihost.master.qerun(runcmd)

    def class_teardown(self, multihost):
        """ Class Teardown """
        teardown_test_prereqs(multihost, prefix=data.PREFIX)

    def test_0001_successfully_remove_container_owner_user_from_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove container owner user from user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-remove-owner', CONTAINER_1,
                  '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0002_successfully_remove_container_owner_group_from_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove container owner group from user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-remove-owner', CONTAINER_1,
                  '--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0003_successfully_remove_container_owner_service_from_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove container owner service from user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-remove-owner', CONTAINER_1,
                  '--services=' + data.PREFIX + '_service1/' + multihost.master.hostname]
        multihost.master.qerun(runcmd)

    def test_0004_fail_to_remove_container_owner_user_already_removed_from_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove container owner user not a member from user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-remove-owner', CONTAINER_1,
                  '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="not a member")

    def test_0005_fail_to_remove_container_owner_user_not_a_member_from_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove container owner user not a member from user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-remove-owner', CONTAINER_1,
                  '--users=' + data.PREFIX + '_user3']
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="not a member")

    def test_0006_fail_to_remove_container_owner_group_not_a_member_from_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove container owner group not a member from user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-remove-owner', CONTAINER_1,
                  '--groups=' + data.PREFIX + '_group3']
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="not a member")

    def test_0007_fail_to_remove_container_owner_service_not_a_member_from_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove container owner service not a member from user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-remove-owner', CONTAINER_1,
                  '--services=' + data.PREFIX + '_service3/' + multihost.master.hostname]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="not a member")

    def test_0008_fail_to_remove_container_owner_user_from_non_existent_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove container owner user from non_existent user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-remove-owner', CONTAINER_DNE_INVALID_USER,
                  '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="not found")

    def test_0009_fail_to_remove_container_owner_group_from_non_existent_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove container owner group from non_existent user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-remove-owner', CONTAINER_DNE_INVALID_USER,
                  '--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="not found")

    def test_0010_fail_to_remove_container_owner_service_from_non_existent_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove container owner service from non_existent user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_DNE_INVALID_USER,
                  '--services=' + data.PREFIX + '_service1/' + multihost.master.hostname]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="not found")


class TestUserVaultContainerOwnerShow(object):
    """
    User Vault Container Owner Show Tests
    """

    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'user_container_show')
        setup_test_prereqs(multihost, prefix=data.PREFIX)

        global CONTAINER_1
        global CONTAINER_DNE_INVALID_USER
        global CONTAINER_DNE_VALID_USER
        CONTAINER_1 = '--user=testuser1'
        CONTAINER_DNE_INVALID_USER = '--user=dne'
        CONTAINER_DNE_VALID_USER = '--user=' + data.PREFIX + '_user1'

        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1,
                  '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def class_teardown(self, multihost):
        """ Class Teardown """
        teardown_test_prereqs(multihost, prefix=data.PREFIX)

    def test_0001_successfully_show_container_owners_for_existing_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully show container owners for existing user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-show', CONTAINER_1]
        multihost.master.qerun(runcmd, exp_output=data.PREFIX + '_user1')

    def test_0002_fail_to_show_container_owners_for_non_existent_user_container_for_valid_user(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to show container owners for non_existent user container for valid user

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-show', CONTAINER_DNE_VALID_USER]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output='not found')

    def test_0003_fail_to_show_container_owners_for_non_existent_user_container_for_invalid_user(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to show container owners for non_existent user container for invalid user

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-show', CONTAINER_DNE_INVALID_USER]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output='not found')


class TestUserVaultContainerDelete(object):
    """
    User Vault Container  Delete Tests
    """
    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'user_container_del')
        setup_test_prereqs(multihost, prefix=data.PREFIX)

        global CONTAINER_1
        global CONTAINER_2
        global CONTAINER_DNE_INVALID_USER
        global CONTAINER_DNE_VALID_USER
        CONTAINER_1 = '--user=' + data.PREFIX + '_user1'
        CONTAINER_2 = '--user=' + data.PREFIX + '_user2'
        CONTAINER_DNE_INVALID_USER = '--user=dne'
        CONTAINER_DNE_VALID_USER = '--user=' + data.PREFIX + '_user3'

        runcmd = ['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_empty',
                  CONTAINER_1]
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-del', data.PREFIX + '_vault_empty', CONTAINER_1]
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_non_empty',
                  CONTAINER_2]
        multihost.master.qerun(runcmd)

    def class_teardown(self, multihost):
        """ Class Teardown """
        teardown_test_prereqs(multihost, prefix=data.PREFIX)

    def test_0001_successfully_delete_container_for_empty_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully delete container for empty user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-del', CONTAINER_1]
        multihost.master.qerun(runcmd)

    def test_0002_fail_to_delete_container_for_non_empty_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to delete container for non_empty user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-del', CONTAINER_2]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="Not allowed")

    def test_0003_fail_to_delete_container_for_non_existent_user_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to delete container for non_existent user container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-del', CONTAINER_DNE_VALID_USER]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="not found")
