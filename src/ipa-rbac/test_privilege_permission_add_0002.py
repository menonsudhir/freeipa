"""
Overview:
Test suite to verify rbac privilege-add-permission option
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.privilege_utils import privilege_add, privilege_del
from ipa_pytests.shared.privilege_utils import privilege_add_permission
from ipa_pytests.shared.permission_utils import permission_add, permission_del


class TestPrivilegeAddPermissionNegative(object):
    """
    Negative testcases related to permission-add-permission
    """

    privilege_name = "Add User"
    permission_name = "Add HBAC rule"

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_setup(self, multihost):
        """
        Setup step for the Privilege add negative test phase
        :param multihost:
        :return:
        """
        privilege_desc = "--desc=Add User"
        privilege_add(multihost.master, self.privilege_name, [privilege_desc])
        permission_add(multihost.master, self.permission_name,
                       ['--right=all',
                        '--targetgroup=groupone'])
        privilege_add_permission(multihost.master, self.privilege_name,
                                 ['--permission=' + self.permission_name])

    def test_0001_nonexistent_permission_add(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add nonexistent permission to privilege
        """
        privilege_name = "Add User"
        permission_name = "non-existent"
        expmsg = "permission: " + permission_name + ": permission not found"
        check1 = privilege_add_permission(multihost.master, privilege_name,
                                          ['--permission=' + permission_name],
                                          False)
        if expmsg not in check1.stdout_text:
            pytest.fail("Adding non existent permission to " + privilege_name +
                        " should have failed")

    def test_0002_duplicate_permission_to_privilege(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add duplicate permission to privilege
        """
        privilege_name = "Add User"
        permission_name = "Add HBAC rule"
        expmsg = "permission: " + permission_name + ": This entry is already a member"
        check2 = privilege_add_permission(multihost.master, privilege_name,
                                          ['--permission=' + permission_name],
                                          False)
        if expmsg not in check2.stdout_text:
            pytest.fail("Adding duplicate permission to " + privilege_name +
                        " should have failed")

    def test_0003_add_permission_nonexistent_privilege(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add permission to nonexistent privilege
        """
        permission_name = "Add HBAC rule"
        privilege_name = "non-existent privilege"
        expmsg = "ipa: ERROR: " + privilege_name + ": privilege not found"
        check3 = privilege_add_permission(multihost.master, privilege_name,
                                          ['--permission=' + permission_name],
                                          False)
        if expmsg not in check3.stderr_text:
            pytest.fail("Adding permission to " + privilege_name + " should have failed")

    def test_cleanup(self, multihost):
        """
        Cleanup
        :param multihost:
        :return:
        """
        privilege_del(multihost.master, self.privilege_name)
        permission_del(multihost.master, self.permission_name)
