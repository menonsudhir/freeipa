"""
Overview:
Test suite to verify rbac role-remove-member option
"""
from __future__ import print_function
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.role_utils import role_remove_member
import pytest


class TestRoleRemoveMemberNegative(object):
    """
    Negative testcases related to role-remove-member
    """

    role_name = "helpdesk"

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_blank_hostgroup_members(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to remove blank hostgroup members
        """
        check1 = role_remove_member(multihost.master, self.role_name,
                                    ['--hostgroups='])
        expmsg = "Number of members removed 0"
        if expmsg not in check1.stdout_text:
            pytest.fail("This test should have failed")

    def test_0002_missing_group_members(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to remove missing group members
        """
        check2 = role_remove_member(multihost.master, self.role_name,
                                    ['--groups='])
        expmsg = "Number of members removed 0"
        if expmsg not in check2.stdout_text:
            pytest.fail("This test should have failed")
