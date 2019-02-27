"""
Overview:
Test suite cover the functional tests of Role Based Access Control
which has 3 sets of clis: privilege, privilege and role
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.permission_utils import permission_add, permission_del, permission_mod
from ipa_pytests.shared.user_utils import add_ipa_user, del_ipa_user
from ipa_pytests.shared.role_utils import role_add_member, role_add_privilege, role_add
from ipa_pytests.shared.role_utils import role_del, role_mod
from ipa_pytests.shared.paths import IPA
from ipa_pytests.shared.privilege_utils import privilege_add, privilege_add_permission
from ipa_pytests.shared.privilege_utils import privilege_del


class TestFunctional2(object):
    """
    Testcases related to functional test of rbac
    """
    login2 = "testgroupdescadmin"
    firstname2 = "testgroupdescadmin"
    lastname2 = "testgroupdescadmin"
    password2 = "Secret123"
    groupname2 = "groupone"
    perm_rights = "--right=write"
    perm_target = "--targetgroup=groupone"
    perm_attr = "--attr=description"
    perm_name = "ManageGroupDescAndUsers"
    priv_name = "Modify Group Desc And Users"
    priv_desc = "--desc=Modify Group Desc And Users"
    perm_name_priv = "--permission=" + perm_name
    role_name = "Test Group Desc Admin"
    role_desc = "--desc=Test Group Desc Admin"
    new_user = "temp_user"
    role_mod_name = "Test Group Desc And User Admin"

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_setup(self, multihost):
        """
                Setup common to all functions
                :param multihost:
                :return:
        """
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master,
                     self.login2,
                     self.password2,
                     self.firstname2,
                     self.lastname2)
        permission_add(multihost.master,
                       self.perm_name,
                       [self.perm_rights, self.perm_target, self.perm_attr])
        privilege_add(multihost.master,
                      self.priv_name,
                      [self.priv_desc])
        privilege_add_permission(multihost.master,
                                 self.priv_name,
                                 [self.perm_name_priv])
        role_add(multihost.master,
                 self.role_name,
                 [self.role_desc])
        role_add_privilege(multihost.master,
                           self.role_name,
                           ['--privileges='+self.priv_name])
        role_add_member(multihost.master,
                        self.role_name,
                        ['--users='+self.login2, '--all'])
        add_ipa_user(multihost.master,
                     self.new_user,
                     "Secret123",
                     'new',
                     'user')

    def test_0001(self, multihost):
        """IDM-IPA-TC : rbac : Modify group desc allowed but adding user not allowed"""
        multihost.master.kinit_as_user(self.login2, self.password2)
        new_desc = "--desc=Updated Group One"
        check2_1 = multihost.master.run_command([IPA, 'group-mod', self.groupname2,
                                                 new_desc], raiseonerr=False)
        if check2_1.returncode:
            pytest.fail(check2_1.stderr_text)
        else:
            print("group modification done successfully")
        check2_1a = multihost.master.run_command([IPA, 'group-add-member',
                                                  self.groupname2,
                                                  '--users='+self.new_user],
                                                 raiseonerr=False)
        exp_output2_1 = "Number of members added 0"
        if exp_output2_1 in check2_1a.stdout_text:
            print("adding member to the group failed as expected")
        else:
            pytest.fail(check2_1a.stderr_text)

    # Marking this as xfail because of bug in 389-ds-base:
    # https://bugzilla.redhat.com/show_bug.cgi?id=1678517
    #
    # When this is fixed, will need to complete this ticket:
    # https://projects.engineering.redhat.com/browse/FREEIPA-2557
    #
    @pytest.mark.xfail(reason='BZ#1678517 FREEIPA-2557')
    def test_0002(self, multihost):
        """IDM-IPA-TC : rbac : Add a member to the group by modifying permission of the user"""
        multihost.master.kinit_as_admin()
        permission_mod(multihost.master, self.perm_name, ['--attrs=description',
                                                          '--attrs=member'])
        role_mod(multihost.master, self.role_name, ['--setattr=cn='+self.role_mod_name,
                                                    '--all'])
        multihost.master.kinit_as_user(self.login2, self.password2)
        check2_2 = multihost.master.run_command([IPA, 'group-add-member',
                                                 self.groupname2,
                                                 '--users='+self.new_user],
                                                raiseonerr=False)
        if check2_2.returncode:
            pytest.fail(check2_2.stderr_text)
        else:
            print("new member added successfully to the group")

    # Marking this as xfail because of bug in 389-ds-base:
    # https://bugzilla.redhat.com/show_bug.cgi?id=1678517
    #
    # When this is fixed, will need to complete this ticket:
    # https://projects.engineering.redhat.com/browse/FREEIPA-2557
    #
    @pytest.mark.xfail(reason='BZ#1678517 FREEIPA-2557')
    def test_cleanup(self, multihost):
        """
        Clean up all the test privileges, permissions and roles added
        :param multihost:
        :return:
        """
        multihost.master.kinit_as_admin()
        role_del(multihost.master, self.role_mod_name)
        privilege_del(multihost.master, self.priv_name)
        permission_del(multihost.master, self.perm_name)
        del_ipa_user(multihost.master, self.login2)
        del_ipa_user(multihost.master, self.new_user)
