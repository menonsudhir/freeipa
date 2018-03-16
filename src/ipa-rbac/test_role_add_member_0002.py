"""
Overview:
Test suite to verify rbac role-add-member option
"""
from __future__ import print_function
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.role_utils import role_add_member, role_remove_member
import pytest
from ipa_pytests.shared.paths import IPA


class TestRoleAddMemberNegative(object):
    """
    Negative testcases related to role-add-member
    """

    role_name = "helpdesk"

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_nonexistent_user(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to add nonexistent user member
        """
        login = "nonexistentuser"
        role_type = "--users="
        check1 = role_add_member(multihost.master, self.role_name,
                                 [role_type + login,
                                  '--all'],
                                 False)
        expmsg1 = "member user: " + login + ": no such entry"
        expmsg2 = "Number of members added 0"
        if expmsg1 not in check1.stdout_text or expmsg2 not in check1.stdout_text:
            pytest.fail("This test should have failed")

    def test_0002_missing_user(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to add missing user member
        """
        login = ""
        role_type = "--users="
        check2 = role_add_member(multihost.master, self.role_name,
                                 [role_type+login,
                                  "--all"],
                                 False)
        expmsg = "Number of members added 0"
        if expmsg not in check2.stdout_text:
            pytest.fail("This test should have failed")

    def test_0003_nonexistent_group(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to add nonexistent group member
        """
        group_name = "nonexistentgroup"
        role_type = "--groups="
        check3 = role_add_member(multihost.master, self.role_name,
                                 [role_type+group_name,
                                  "--all"],
                                 False)
        expmsg1 = "member group: " + group_name + ": no such entry"
        expmsg2 = "Number of members added 0"
        if expmsg1 not in check3.stdout_text or expmsg2 not in check3.stdout_text:
            pytest.fail("This test should have failed")

    def test_0004_duplicate_group(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to add duplicate group member
        """
        group_name = "testgroupadmin"
        role_type = "--groups="
        group_desc = "--desc=testgroupadmin"
        multihost.master.run_command([IPA, 'group-add', group_name, group_desc])
        role_add_member(multihost.master, self.role_name,
                        [role_type+group_name,
                         "--all"])
        check4 = role_add_member(multihost.master, self.role_name,
                                 [role_type+group_name,
                                  "--all"],
                                 False)
        expmsg1 = "member group: " + group_name + ": This entry is already a member"
        expmsg2 = "Number of members added 0"
        role_remove_member(multihost.master, self.role_name, [role_type+group_name])
        multihost.master.run_command([IPA, 'group-del', group_name])
        if expmsg1 not in check4.stdout_text or expmsg2 not in check4.stdout_text:
            pytest.fail("This test should have failed")

    def test_0005_nonexistent_host(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to add nonexistent host member"
        """
        host_name = "nonexistenthost."+multihost.master.domain.name
        role_type = "--hosts="
        check5 = role_add_member(multihost.master, self.role_name,
                                 [role_type+host_name,
                                  "--all"],
                                 False)
        expmsg1 = "member host: " + host_name + ": no such entry"
        expmsg2 = "Number of members added 0"
        if expmsg1 not in check5.stdout_text or expmsg2 not in check5.stdout_text:
            pytest.fail("This test should have failed")

    def test_0006_nonexistent_hostgroup(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to add nonexistent hostgroup member
        """
        hostgroup_name = "nonexistenthostgroup"
        role_type = "--hostgroups="
        check6 = role_add_member(multihost.master, self.role_name,
                                 [role_type+hostgroup_name,
                                  "--all"],
                                 False)
        expmsg1 = "member host group: " + hostgroup_name + ": no such entry"
        expmsg2 = "Number of members added 0"
        if expmsg1 not in check6.stdout_text or expmsg2 not in check6.stdout_text:
            pytest.fail("This test should have failed")
