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
from ipa_pytests.shared.privilege_utils import privilege_add_permission, privilege_show


class TestPrivilegeRemovePermissionPositive(object):
    """
    Positive testcases related to privilege-remove-permission
    """
    permission_list = ["Modify HBAC rule", "Delete HBAC rule", "Add HBAC rule"]
    privilege_name = "Add User"

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_setup(self, multihost):
        privilege_desc = "--desc=Add User"
        privilege_add(multihost.master, self.privilege_name, [privilege_desc])
        for permission in self.permission_list:
            permission_add(multihost.master, permission,
                           ['--right=all',
                            '--targetgroup=groupone'])

            privilege_add_permission(multihost.master, self.privilege_name,
                                     ["--permission=" + permission])

    def test_0001_multiple_permissions(self, multihost):
        """
        IDM-IPA-TC : rbac : Test remove multiple permissions to privilege
        """
        privilege_remove_permission(multihost.master, self.privilege_name,
                                    ['--permission='+self.permission_list[0],
                                     '--permission='+self.permission_list[1]])
        check1 = privilege_show(multihost.master, self.privilege_name)
        if self.permission_list[2] not in check1.stdout_text or self.permission_list[0] in \
                check1.stdout_text or self.permission_list[1] in check1.stdout_text:
            pytest.fail("Error in removing permissions from privilege")

    def test_0002_permission_ipa_privilege(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to remove permission from IPA defined privilege
        """
        privilege_name = "HBAC Administrator"
        permission_name = "Add Group"
        permission_add(multihost.master, permission_name,
                       ['--right=all',
                        '--targetgroup=groupone'])
        privilege_add_permission(multihost.master, privilege_name,
                                 ["--permission=" + permission_name])
        check2 = privilege_remove_permission(multihost.master, privilege_name,
                                             ['--permission='+permission_name])
        if permission_name in check2.stdout_text:
            pytest.fail("Error in removing permission "+permission_name+" from "+privilege_name)
        permission_del(multihost.master, permission_name)

    def test_cleanup(self, multihost):
        """
        Cleanup
        :param multihost:
        :return:
        """
        privilege_del(multihost.master, self.privilege_name)
        for permission in self.permission_list:
            permission_del(multihost.master, permission)
