"""
Vault Admin Privilege tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements

from .lib import setup_test_prereqs, teardown_test_prereqs
import data  # pylint: disable=relative-import
import pytest

VADMIN = ''
NONVADMIN = ''


class TestVaultAdminPrivileges(object):
    """
    Vault Administrators Privileges Tests
    """

    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'admin_privs')
        setup_test_prereqs(multihost, prefix=data.PREFIX)

        global VADMIN
        global NONVADMIN
        VADMIN = data.PREFIX + '_user1'
        NONVADMIN = data.PREFIX + '_user3'

    def class_teardown(self, multihost):
        """ Class Setup """
        teardown_test_prereqs(multihost, prefix=data.PREFIX)
        runcmd = ['ipa', 'role-del', 'vadmins']
        multihost.master.qerun(runcmd)

    def test_0001_create_new_vault_administrators_group(self, multihost):
        """
        IDM-IPA-TC: Vault: Create new Vault Administrators group
        """
        runcmd = ['ipa', 'role-add', 'vadmins']
        multihost.master.qerun(runcmd)
        # need to join with spaces the next command because of the space in the
        # privilege name
        runcmd = ['ipa', 'role-add-privilege', 'vadmins', '--privileges="Vault Administrators"']
        runcmd = " ".join(runcmd)
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'role-add-member', 'vadmins', '--users=' + VADMIN]
        multihost.master.qerun(runcmd)

    def test_0002_add_new_container_owner_with_vault_admin(self, multihost):
        """
        IDM-IPA-TC: Vault: Add new container owner with Vault Admin
        """
        multihost.master.kinit_as_user(VADMIN, data.PASSWORD)
        runcmd = ['ipa', 'vaultcontainer-add-owner', '--user=' + data.USER1,
                  '--users=' + data.PREFIX + '_user2']
        multihost.master.qerun(runcmd)
        multihost.master.kinit_as_admin()

    def test_0003_fail_to_add_container_owner_as_non_admin(self, multihost):
        """
        IDM-IPA-TC: Vault: Fail to add container owner as non_admin
        """
        multihost.master.kinit_as_user(NONVADMIN, data.PASSWORD)
        runcmd = ['ipa', 'vaultcontainer-add-owner', '--user=' + data.USER1,
                  '--users=' + data.PREFIX + '_user3']
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vaultcontainer not found")
        multihost.master.kinit_as_admin()

    def test_0004_fail_to_remove_container_owner_as_non_admin(self, multihost):
        """
        IDM-IPA-TC: Vault: Fail to remove container owner as non_admin
        """
        multihost.master.kinit_as_user(NONVADMIN, data.PASSWORD)
        runcmd = ['ipa', 'vaultcontainer-remove-owner', '--user=' + data.USER1,
                  '--users=' + data.PREFIX + '_user2']
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vaultcontainer not found")
        multihost.master.kinit_as_admin()

    def test_0005_fail_to_add_vault_if_current_user_not_container_owner_or_admin(self, multihost):
        """
        IDM-IPA-TC: Vault: Fail to add vault if current user not container owner or admin
        """
        multihost.master.kinit_as_user(NONVADMIN, data.PASSWORD)
        runcmd = ['ipa', 'vault-add', '--type=standard', 'vault_add_fails', '--user=' + data.USER1]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="Insufficient access")

    def test_0006_fail_to_remove_vault_if_current_user_not_container_owner_or_admin(self, multihost):
        """
        IDM-IPA-TC: Vault: Fail to remove vault if current user not container owner or admin
        """
        multihost.master.kinit_as_user(NONVADMIN, data.PASSWORD)
        runcmd = ['ipa', 'vault-del', data.PREFIX + '_vault_user', '--user=' + data.USER1]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="Insufficient access")
        multihost.master.kinit_as_admin()

    def test_0007_successfully_add_vault_if_current_user_is_container_owner(self, multihost):
        """
        IDM-IPA-TC: Vault:  Successfully add vault if current user is container owner
        """
        multihost.master.kinit_as_user(data.PREFIX + '_user2', data.PASSWORD)
        runcmd = ['ipa', 'vault-add', '--type=standard', '--user=' + data.USER1,
                  data.PREFIX + 'newvault_from_newowner']
        multihost.master.qerun(runcmd)
        multihost.master.kinit_as_admin()

    def test_0008_successfully_remove_vault_if_current_user_is_container_owner(self, multihost):
        """
        IDM-IPA-TC: Vault: Successfully remove vault if current user is container owner
        """
        multihost.master.kinit_as_user(data.PREFIX + '_user2', data.PASSWORD)
        runcmd = ['ipa', 'vault-del', '--user=' + data.USER1, data.PREFIX + 'newvault_from_newowner']
        multihost.master.qerun(runcmd)
        multihost.master.kinit_as_admin()
