"""
Overview:
Test suite to verify rbac role-add-privilege option
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.role_utils import role_add_privilege, role_remove_privilege


class TestRolePrivilegeAddNegative(object):
    """
    Negatice testcases related to role-add-privilege
    """
    role_name = "helpdesk"

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_duplicate_privilege(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to add duplicate privilege to role
        """
        privilege_name = "user administrators"
        privilege_list = "--privileges="+privilege_name
        role_add_privilege(multihost.master, self.role_name,
                           [privilege_list, "--all"])
        check1 = role_add_privilege(multihost.master, self.role_name,
                                    [privilege_list, "--all"], False)
        expmsg1 = "privilege: " + privilege_name + ": This entry is already a member"
        expmsg2 = "Number of privileges added 0"
        role_remove_privilege(multihost.master, self.role_name,
                              [privilege_list,
                               '--all'])
        if expmsg1 not in check1.stdout_text or expmsg2 not in check1.stdout_text:
            pytest.fail("This test should have failed")

    def test_0002_missing_privilege(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to add missing privilege to role
        """
        privilege_name = "nonexistent"
        privilege_list = "--privileges="+privilege_name
        check2 = role_add_privilege(multihost.master, self.role_name,
                                    [privilege_list, "--all"], False)
        expmsg1 = "privilege: " + privilege_name + ": privilege not found"
        expmsg2 = "Number of privileges added 0"
        if expmsg1 not in check2.stdout_text or expmsg2 not in check2.stdout_text:
            pytest.fail("This test should have failed")
