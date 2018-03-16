"""
Overview:
Test suite to verify rbac privilege-remove_permission option
"""

from __future__ import print_function
import pytest
from ipa_pytests.shared.privilege_utils import privilege_remove_permission
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.privilege_utils import privilege_add, privilege_del
from ipa_pytests.shared.permission_utils import permission_add, permission_del


class TestPrivilegeRemovePermissionNegative(object):
    """
    Negative testcases related to privilege-remove-permission
    """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_nonexistent_permission(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to remove nonexistent permission from privilege
        """
        privilege_name = "Add User"
        permission_name = "non-existent permission"
        privilege_add(multihost.master, privilege_name)
        check1 = privilege_remove_permission(multihost.master, privilege_name,
                                             ["--permission=" + permission_name],
                                             False)
        expmsg = "permission: " + permission_name + ": permission not found"
        if expmsg not in check1.stdout_text:
            pytest.fail("Removing nonexistent permission from privilege should have failed")
        privilege_del(multihost.master, privilege_name)

    def test_0002_nonexistent_privilege(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to remove permission from nonexistent privilege
        """
        privilege_name = "non-existent"
        permission_name = "Add HBAC rule"
        permission_add(multihost.master, permission_name,
                       ['--right=all',
                        '--targetgroup=groupone'])
        check2 = privilege_remove_permission(multihost.master, privilege_name,
                                             ["--permission=" + permission_name],
                                             False)
        expmsg = "ipa: ERROR: " + privilege_name + ": privilege not found"
        if expmsg not in check2.stderr_text:
            pytest.fail("Removing permission from nonexistent privilege should have failed")
        permission_del(multihost.master, permission_name)
