"""
Overview:
Test suite to verify rbac role-add-privilege option
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.role_utils import role_add_privilege, role_remove_privilege


class TestRolePrivilegeAddPositive(object):
    """
    Positive testcases related to role-add-privilege
    """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_add_all(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add privilege to role with option all
        """
        privilege_name = "--privileges=User Administrators"
        role_name = "helpdesk"
        role_add_privilege(multihost.master, role_name,
                           [privilege_name,
                            '--all'])

    def test_0002_add_raw(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add multiple privileges to role with option raw
        """
        privilege_name = ["--privileges=group administrators",
                          "--privileges=hbac administrator"]
        role_name = "helpdesk"
        privilege_name.append('--raw')
        role_add_privilege(multihost.master, role_name, privilege_name)

    def test_0003_remove_multiple_privileges_raw(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to remove multiple privileges from role with option raw
        """
        privilege_name = ["--privileges=group administrators",
                          "--privileges=hbac administrator"]
        role_name = "helpdesk"
        privilege_name.append('--raw')
        check3 = role_remove_privilege(multihost.master, role_name, privilege_name)
        nonexpmsg1 = "memberof_privilege: group administrators"
        nonexpmsg2 = "memberof_privilege: hbac administrator"
        expmsg = "Number of privileges removed 2"
        if expmsg not in check3.stdout_text or nonexpmsg1 in check3.stdout_text or nonexpmsg2 \
                in check3.stdout_text:
            pytest.fail("Error, these privileges should have been deleted")

    def test_0004_remove_user_privilege_all(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to remove a user added privilege from role with option all
        """
        role_name = "helpdesk"
        privilege_name = "User Administrators"
        check4 = role_remove_privilege(multihost.master, role_name,
                                       ['--privileges=User Administrators',
                                        '--all'])
        expmsg = "Number of privileges removed 1"
        if expmsg not in check4.stdout_text:
            pytest.fail(privilege_name+" should have been deleted")

    def test_0005_remove_existing_privilege(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to remove an existing privilege from role
        """
        role_name = "helpdesk"
        privilege_name = "Modify Group membership"
        check5 = role_remove_privilege(multihost.master, role_name,
                                       ["--privileges=" + privilege_name,
                                        '--all'])
        expmsg = "Number of privileges removed 1"
        role_add_privilege(multihost.master, role_name,
                           ["--privileges=" + privilege_name,
                            '--all'])
        if expmsg not in check5.stdout_text:
            pytest.fail(privilege_name+" should have been deleted")
