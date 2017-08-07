"""
Shared Vault Container tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements

from .lib import setup_test_prereqs, teardown_test_prereqs
import data  # pylint: disable=relative-import

CONTAINER_1 = []
CONTAINER_2 = []
CONTAINER_DNE_INVALID_USER = []
CONTAINER_DNE_VALID_USER = []


class TestSharedVaultContainerAddOwner(object):
    """
    Shared Vault Container Add Owner Tests
    """

    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'shared_container_add')
        setup_test_prereqs(multihost, prefix=data.PREFIX)
        global CONTAINER_1
        CONTAINER_1 = '--shared'

    def class_teardown(self, multihost):
        """ Class Teardown """
        teardown_test_prereqs(multihost, prefix=data.PREFIX)

    def test_0001_successfully_add_container_owner_user_to_shared_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add container owner user to shared container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1,
                  '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0002_successfully_add_container_owner_group_to_shared_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add container owner group to shared container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1,
                  '--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0003_successfully_add_container_owner_service_to_shared_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add container owner service to shared container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1,
                  '--services=' + data.PREFIX + '_service1/' + multihost.master.hostname]
        multihost.master.qerun(runcmd)

    def test_0004_fail_to_add_container_owner_non_existent_user_to_shared_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add container owner non_existent user to shared container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1, '--users=dne']
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="no such entry")

    def test_0005_fail_to_add_container_owner_non_existent_group_to_shared_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add container owner non_existent group to shared container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1, '--groups=dne']
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="no such entry")

    def test_0006_fail_to_add_container_owner_non_existent_service_to_shared_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add container owner non_existent service to shared container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1,
                  '--services=dne/' + multihost.master.hostname]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="no such entry")


class TestSharedVaultContainerRemoveOwner(object):
    """
    Shared Vault Container Remove Owner Tests
    """

    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'shared_container_remove')
        setup_test_prereqs(multihost, prefix=data.PREFIX)
        global CONTAINER_1
        CONTAINER_1 = '--shared'

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

    def test_0001_successfully_remove_container_owner_user_from_shared_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove container owner user from shared container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-remove-owner', CONTAINER_1,
                  '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

    def test_0002_successfully_remove_container_owner_group_from_shared_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove container owner group from shared container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-remove-owner', CONTAINER_1,
                  '--groups=' + data.PREFIX + '_group1']
        multihost.master.qerun(runcmd)

    def test_0003_successfully_remove_container_owner_service_from_shared_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully remove container owner service from shared container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-remove-owner', CONTAINER_1,
                  '--services=' + data.PREFIX + '_service1/' + multihost.master.hostname]
        multihost.master.qerun(runcmd)

    def test_0004_fail_to_remove_container_owner_user_already_removed_from_shared_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove container owner user not a member from shared container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-remove-owner', CONTAINER_1,
                  '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="not a member")

    def test_0005_fail_to_remove_container_owner_user_not_a_member_from_shared_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove container owner user not a member from shared container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-remove-owner', CONTAINER_1,
                  '--users=' + data.PREFIX + '_user3']
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="not a member")

    def test_0006_fail_to_remove_container_owner_group_not_a_member_from_shared_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove container owner group not a member from shared container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-remove-owner', CONTAINER_1,
                  '--groups=' + data.PREFIX + '_group3']
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="not a member")

    def test_0007_fail_to_remove_container_owner_service_not_a_member_from_shared_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to remove container owner service not a member from shared container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-remove-owner', CONTAINER_1,
                  '--services=' + data.PREFIX + '_service3/' + multihost.master.hostname]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="not a member")


class TestSharedVaultContainerShowOwner(object):
    """
    Shared Vault Container Owner Show Tests
    """
    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'shared_container_show')
        setup_test_prereqs(multihost, prefix=data.PREFIX)
        global CONTAINER_1
        CONTAINER_1 = '--shared'
        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1,
                  '--users=' + data.PREFIX + '_user1']
        multihost.master.qerun(runcmd)

        runcmd = ['ipa', 'vaultcontainer-add-owner', CONTAINER_1,
                  '--services=' + data.PREFIX + '_service1/' + multihost.master.hostname]
        multihost.master.qerun(runcmd)

    def class_teardown(self, multihost):
        """ Class Teardown """
        teardown_test_prereqs(multihost, prefix=data.PREFIX)

    def test_0001_successfully_show_container_owners_for_shared_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully show container owners for shared container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-show', CONTAINER_1]
        multihost.master.qerun(runcmd, exp_output=data.PREFIX + '_service1')


class TestSharedVaultContainerDelete(object):
    """
    Shared Vault Container  Delete Tests
    """
    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'shared_container_del')
        setup_test_prereqs(multihost, prefix=data.PREFIX)
        global CONTAINER_1
        CONTAINER_1 = '--shared'

        runcmd = ['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_empty',
                  CONTAINER_1]
        multihost.master.qerun(runcmd)

    def class_teardown(self, multihost):
        """ Class Teardown """
        teardown_test_prereqs(multihost, prefix=data.PREFIX)

    def test_0001_fail_to_delete_container_for_non_empty_shared_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to delete container for non_empty shared container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultcontainer-del', CONTAINER_1]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="Not allowed")

    def test_0002_successfully_delete_container_for_empty_shared_container(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully delete container for empty shared container

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-del', data.PREFIX + '_vault_empty', CONTAINER_1]
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vaultcontainer-del', CONTAINER_1]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="Not allowed")
