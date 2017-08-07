"""
Vault Container Miscellaneous Functional tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements

from ipa_pytests.shared.user_utils import add_ipa_user
from .lib import setup_test_prereqs, teardown_test_prereqs
import data  # pylint: disable=relative-import

data.PREFIX = ''
data.DNE_VAULT = []
data.PRIV_VAULT = []
data.USER_VAULT = []
data.SHARED_VAULT = []
data.SERVICE_VAULT = []


class TestVaultContainerMiscFunc(object):
    """
    Vault Container Miscellaneous Functional Tests
    """

    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'cont_misc_func')
        setup_test_prereqs(multihost, prefix=data.PREFIX)
        add_ipa_user(multihost.master, 'orphan1', data.PASSWORD)
        add_ipa_user(multihost.master, 'orphan2', data.PASSWORD)

    def class_teardown(self, multihost):
        """ Class Teardown """
        teardown_test_prereqs(multihost, prefix=data.PREFIX)
        runcmd = ['ipa', 'user-del', 'orphan1']
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'user-del', 'orphan2']
        multihost.master.qerun(runcmd)

    def test_0001_fail_to_create_user_container_with_different_unprivileged_user_running_vault_add(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault:  Fail to create user container with different unprivileged user running vault-add

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        multihost.master.kinit_as_user(data.PREFIX + '_user1', data.PASSWORD)
        runcmd = ['ipa', 'vault-add', '--type=standard', '--user=' + data.PREFIX + '_user2',
                  data.PREFIX + 'newvault_from_diff_user']
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="Insufficient access")
        multihost.master.kinit_as_admin()

    def test_0002_fail_to_show_orphaned_container_with_unprivileged_user(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault:  Fail to show orphaned container with unprivileged user

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-add', '--type=standard', 'orphan_vault', '--user=orphan1']
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-del', 'orphan_vault', '--user=orphan1']
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vaultcontainer-show', '--user=orphan1']
        multihost.master.qerun(runcmd)
        multihost.master.kinit_as_user('orphan2', data.PASSWORD)
        runcmd = ['ipa', 'vaultcontainer-show', '--user=orphan1']
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="not found")
