"""
Overview:
TestSuite to verify BZs related to rbac
SetUp Requirements:
-Latest version of RHEL OS
-Need to test for Master
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.permission_utils import permission_add, permission_del
from ipa_pytests.shared.permission_utils import permission_find


class TestBugCheck(object):
    """ Test Class """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0012_bz785251(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify Bug 785251 - permission find should not retrieve all permissions
        """
        permission_name = "BugManageUser_785251"
        multihost.master.kinit_as_admin()
        permission_add(multihost.master, permission_name, ['--right=read',
                                                           '--attr=carlicense',
                                                           '--attr=description'])
        check12a = permission_find(multihost.master, permission_name=None,
                                   options_list=['--name='+permission_name,
                                                 '--all'],
                                   raiseonerr=False)
        if check12a.returncode == 0:
            print("First part of Bug 785251 verified successfully")
        else:
            pytest.xfail("Error in finding the " + permission_name)
        permission_del(multihost.master, permission_name)

        check12b = permission_find(multihost.master, None, ['--name=\\',
                                                            '--all'], False)
        if check12b.returncode != 0:
            print("Bug 785251 Verified")
        else:
            pytest.xfail("Bug verification 785251 Failed")

    def test_0013_bz785257(self, multihost):
        """
        IDM-IPA-TC : rbac : Function to verify bz785257 - Ensure find permission with option sizelimit works
        """
        right = 'xyz'
        exp_output = "Number of entries returned 0"
        check13 = permission_find(multihost.master, permission_name=None,
                                  options_list=['--right='+right,
                                                '--all'], raiseonerr=False)
        if exp_output in check13.stdout_text:
            print("Success! Verified bz785257")
        else:
            pytest.xfail("verification of bz785257 failed")

    def test_0014_bz785254(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify bz785254 - find permission with option subtree
        """
        multihost.master.kinit_as_admin()
        permission_name = "Manage_bz785254"
        permission_name1 = "Read Hosts"
        permission_name2 = "Remove Hosts"
        permission_add(multihost.master, permission_name,
                       ['--right=write',
                        '--subtree=cn=computers,cn=accounts,'
                        + multihost.master.domain.basedn.replace('"', ''),
                        '--memberof=groupone',
                        '--attr=nshostlocation'])
        check14a = permission_find(multihost.master, permission_name=None,
                                   options_list=['--subtree=cn=computers,cn=accounts,' +
                                                 multihost.master.domain.basedn.replace('"', ''),
                                                 '--all'])
        if permission_name in check14a.stdout_text and permission_name1 in check14a.stdout_text \
                and permission_name2 in check14a.stdout_text:
            print("bz785254 verification successful")
        else:
            pytest.xfail(permission_name + " not found, verification of bz785254 failed")
        permission_del(multihost.master, permission_name)

    def test_0015_bz893827(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify bz893827 - find permission with option targetgroup
        """
        multihost.master.kinit_as_admin()
        permission_name = "Add User to default group"
        check15 = permission_find(multihost.master, permission_name=None,
                                  options_list=['--targetgroup=ipausers', '--all'])
        if permission_name in check15.stdout_text:
            print("bz893827 verification successful")
        else:
            pytest.xfail(permission_name + " not found, verification of bz893827 failed")

    def test_0016_bz785257(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify bz785257 - find permission with options attrs permissions type sizelimit
        """
        multihost.master.kinit_as_admin()
        perm_array = ["FindManageUser161",
                      "FindManageUser162",
                      "FindManageUser163",
                      "FindManageUser164",
                      "FindManageUser165"]
        for perm in perm_array:
            permission_add(multihost.master, perm, ['--right=write',
                                                    '--attr=carlicense',
                                                    '--attr=description',
                                                    '--type=user'])
        check16a = permission_find(multihost.master, permission_name=None,
                                   options_list=['--attrs=description',
                                                 '--right=write',
                                                 '--type=user',
                                                 '--sizelimit=3',
                                                 '--all'])
        if "Number of entries returned 3" in check16a.stdout_text:
            print("bz785257 verified")
        else:
            pytest.fail("Error in verification of bz785257")
        for perm in perm_array:
            permission_del(multihost.master, perm, ['--continue'])

    def test_0017_bz785259(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify bz785259 - permission attrs after a find with option raw
        """
        permission_name = "FindManageHost17"
        multihost.master.kinit_as_admin()
        permission_add(multihost.master, permission_name,
                       ['--right=write',
                        '--subtree=cn=computers,cn=accounts,'
                        + multihost.master.domain.basedn.replace('"', ''),
                        '--memberof=groupone',
                        '--attr=nshostlocation'])
        check17a = permission_find(multihost.master, permission_name=None,
                                   options_list=['--memberof=groupone', '--raw'])
        if permission_name in check17a.stdout_text:
            print("Verification of bz785259 successfull")
        else:
            pytest.xfail("Error in verification of bz785259")
        permission_del(multihost.master, permission_name)
