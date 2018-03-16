"""
Overview:
Test suite to verify rbac privilege-add-permission option
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.permission_utils import permission_add, permission_del
from ipa_pytests.shared.privilege_utils import privilege_add, privilege_add_permission
from ipa_pytests.shared.privilege_utils import privilege_del, privilege_remove_permission


class TestPrivilegeAddPermissionPositive(object):
    """
    Positive testcases related to privilege-add-permission
    """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_multiple_permission(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add multiple permissions to privilege
        """
        privilege_name = "Add User"
        privilege_add(multihost.master, privilege_name)
        permission_list = ["Modify HBAC rule", "Delete HBAC rule", "Add HBAC rule"]
        for permission in permission_list:
            permission_add(multihost.master, permission,
                           ['--right=all',
                            '--targetgroup=groupone'])

        privilege_add_permission(multihost.master, privilege_name,
                                 ["--permission="+permission_list[0],
                                  "--permission="+permission_list[1],
                                  "--permission="+permission_list[2]])

        privilege_del(multihost.master, privilege_name)
        for permission in permission_list:
            permission_del(multihost.master, permission)

    def test_0002_add_permission_ipa_privilege(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add permission to IPA provided privilege
        """
        privilege_name = "HBAC Administrator"
        permission_name = "Add Group"
        permission_add(multihost.master, permission_name,
                       ['--right=all',
                        '--targetgroup=groupone'])
        check2 = privilege_add_permission(multihost.master, privilege_name,
                                          ["--permission=" + permission_name])
        if permission_name not in check2.stdout_text:
            pytest.fail("Adding " + permission_name + " to " + privilege_name + " failed")
        privilege_remove_permission(multihost.master, privilege_name,
                                    ['--permission='+permission_name])
        permission_del(multihost.master, permission_name)
