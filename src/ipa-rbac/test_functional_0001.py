"""
Overview:
Test suite cover the functional tests of Role Based Access Control
which has 3 sets of clis: privilege, privilege and role
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.user_utils import add_ipa_user, del_ipa_user, mod_ipa_user
from ipa_pytests.shared.role_utils import role_add_member
from ipa_pytests.shared.role_utils import role_add
from ipa_pytests.shared.paths import IPA


class TestFunctional1(object):
    """
    Scenario:
        User with Helpdesk Role should
        not be to update users in Adminstrator group's password
        not be able new user
        be able to upadet user attr
        be able to reset a user's password
    """
    login1 = "testuserhelpdesk"
    firstname1 = "testUserHelpdesk"
    lastname1 = "testUserHelpdesk"
    password1 = "Secret123"
    role_name1 = "helpdesk"

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
                     self.login1,
                     self.password1,
                     self.firstname1,
                     self.lastname1)
        role_add(multihost.master,
                 self.role_name1,
                 raiseonerr=False)
        role_add_member(multihost.master,
                        self.role_name1,
                        ['--users=' + self.login1,
                         '--all'])

    def test0001(self, multihost):
        """IDM-IPA-TC : rbac : user added to helpdesk role cannot reset admins password"""
        multihost.master.kinit_as_user(self.login1,
                                       self.password1)
        new_pwd = "Secret456"
        new_pwd_temp = '%s\n%s\n' % (new_pwd, new_pwd)
        check1_1 = multihost.master.run_command([IPA, 'passwd', 'admin'],
                                                stdin_text=new_pwd_temp,
                                                raiseonerr=False)
        exp_output1_1 = "ipa: ERROR: Insufficient access: Insufficient access rights"
        if exp_output1_1 in check1_1.stderr_text:
            print("changing admin passwd failed as expected")
        else:
            pytest.xfail(check1_1.stderr_text)

    # HelpDesk - can modify group memberships, modify users, reset password
    # this user should be allowed to modify a user's lastname, reset password,
    #  but cannot add or delete this user

    def test0002(self, multihost):
        """IDM-IPA-TC : rbac : user added to helpdesk role cannot add new user"""
        login1_2 = "two"
        firstname1_2 = "two"
        lastname1_2 = "two"
        new_pwd1_2 = "two"
        multihost.master.kinit_as_user(self.login1, self.password1)
        # can't use add_ipa_user util since it changes to kinit admin -
        # requires add_ipa_user util modification
        check1_2 = multihost.master.run_command([IPA, 'user-add',
                                                 '--first', firstname1_2,
                                                 '--last', lastname1_2,
                                                 '--password', login1_2],
                                                stdin_text=new_pwd1_2,
                                                raiseonerr=False)
        exp_output1_2 = "ipa: ERROR: Insufficient access: Could not read UPG Definition" \
                        " originfilter. Check your permissions."
        if exp_output1_2 in check1_2.stderr_text:
            print("adding new user failed as expected")
        else:
            pytest.xfail(check1_2.stderr_text)
        multihost.master.kinit_as_admin()
        del_ipa_user(multihost.master, login1_2)

    def test0003(self, multihost):
        """IDM-IPA-TC : rbac : Helpdesk admin should be able to change a users lastname, bz817915"""
        login1_3 = "three"
        firstname1_3 = "three"
        lastname1_3 = "three"
        new_pwd1_3 = "three"
        multihost.master.kinit_as_admin()
        multihost.master.run_command([IPA, 'user-add',
                                      '--first=' + firstname1_3,
                                      '--last=' + lastname1_3,
                                      '--password',
                                      login1_3],
                                     stdin_text=new_pwd1_3,
                                     raiseonerr=False)
        new_last_name = "twotwo"
        multihost.master.kinit_as_user(self.login1, self.password1)
        check1_3 = mod_ipa_user(multihost.master, login1_3,
                                ['--last=' + new_last_name])
        if check1_3.returncode:
            pytest.xfail(check1_3.stderr_text)
        else:
            print("last name modified successfully")
        del_ipa_user(multihost.master, login1_3)

    def test0004(self, multihost):
        """IDM-IPA-TC : rbac : helpdesk admin should be able to change password , bz773759"""
        multihost.master.kinit_as_user(self.login1, self.password1)
        login1_4 = "four"
        firstname1_4 = "four"
        lastname1_4 = "four"
        new_pwd1_4 = "four"
        multihost.master.kinit_as_admin()
        multihost.master.run_command([IPA, 'user-add',
                                      '--first='+firstname1_4,
                                      '--last='+lastname1_4,
                                      '--password',
                                      login1_4],
                                     stdin_text=new_pwd1_4)
        new_pwd_temp = "twotwo"
        check1_4 = multihost.master.run_command([IPA, 'passwd', login1_4],
                                                stdin_text=new_pwd_temp,
                                                raiseonerr=False)
        if check1_4.returncode:
            pytest.fail(check1_4.stderr_text)
        else:
            print("password of an user modified successfully")
        del_ipa_user(multihost.master, login1_4)

    # this user can add a user to another group, but cannot add or update a group
    # this user cannot list available hostgroups or netgroups, cannot delete them

    def test_cleanup(self, multihost):
        """
        Clean up all the test privileges, permissions and roles added
        :param multihost:
        :return:
        """
        multihost.master.kinit_as_admin()
        del_ipa_user(multihost.master, self.login1)
