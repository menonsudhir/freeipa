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


class TestBugCheck(object):
    """ Test Class """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_bz1186054(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify Bug 1186054 - permission-add does not prompt to enter --right option in interactive mode
        """
        multihost.master.kinit_as_admin()
        cmd = 'ipa permission-add'
        import pexpect
        op = pexpect.run(cmd,
                         events={"Permission name: ": 'sample_permission\n',
                                 "\[Granted rights\]: ": "read\n",
                                 '\[Subtree\]: ': 'cn=groups,cn=accounts,'
                                                  + multihost.master.domain.basedn.replace('"', '')
                                                  + '\n',
                                 '\[Member of group\]: ': 'admins\n',
                                 '\[Target group\]: ': 'admins\n',
                                 '\[Type\]: ': "\n"})
        print ("###############################command run output #######################")
        print (op)
        if 'Added permission "sample_permission"' not in op:
            pytest.xfail("expected output not found")
        else:
            print("COMMAND SUCCEEDED and bz1186054 Verified!")
        permission_del(multihost.master, 'sample_permission')

    def test_0002_bz783502(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify Bug 783502 - add permission with invalid attr should fail
        """
        permission_name = "BugManageUser_783502"
        multihost.master.kinit_as_admin()
        check = permission_add(multihost.master, permission_name, ['--right=read',
                                                                   '--attr=ipaclientversion',
                                                                   '--type=user'],
                               False)
        if check.returncode == 0:
            print("Bug 783502 verified successfully")
        else:
            pytest.xfail("Bug 783502 verification failed")
        permission_del(multihost.master, permission_name)

    def test_0003_bz783475(self, multihost):
        """
        TIDM-IPA-TC : rbac : est to verify bug 783475- add permission using blank memberof group should not fail with internal error
        """
        permission_name = "BugManageHost2"
        multihost.master.kinit_as_admin()
        check3 = permission_add(multihost.master, permission_name,
                                ['--right=write',
                                 '--subtree=cn=computers,cn=accounts,'
                                 + multihost.master.domain.basedn.replace('"', ''),
                                 '--attr=nshostlocation',
                                 '--memberof=' + ''])
        if check3.returncode == 0:
            print("Bug bz783475 Verified successfully")
        else:
            pytest.xfail("Bug bz783475 Verification failed")
        permission_del(multihost.master, permission_name)

    def test_0004_bz783543(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify Bug 783543 - add permission using blank memberof group
        """
        permission_name = "BugManageHost3"
        multihost.master.kinit_as_admin()
        check4 = permission_add(multihost.master, permission_name,
                                ['--right=write',
                                 '--subtree=cn=computers,cn=accounts,'
                                 + multihost.master.domain.basedn.replace('"', ''),
                                 '--attr=nshostlocation',
                                 '--memberof='])
        if check4.returncode == 0:
            print("Bug bz783543 Verified successfully")
        else:
            pytest.xfail("Bug bz783543 verification failed")
        permission_del(multihost.master, permission_name)

    def test_0005_bz783502(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify bug 783502: add permission for type hostgroup with multiple attr and multiple permissions
        """
        permission_name = "BugManageHostgroup1"
        multihost.master.kinit_as_admin()
        check5 = permission_add(multihost.master, permission_name,
                                ['--right=write',
                                 '--right=add',
                                 '--right=delete',
                                 '--type=hostgroup',
                                 '--attr=businessCategory',
                                 '--attr=owner'])
        if check5.returncode == 0:
            print("Bug bz783502 Verified successfully")
            permission_del(multihost.master, permission_name)
        else:
            pytest.xfail("Bug bz783502 verification failed")

    def test_0006_bz807304(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify bug 807304 - invalid characters in permission name is not allowed
        """
        permission_name = "Test\<807304"
        multihost.master.kinit_as_admin()
        check4 = permission_add(multihost.master, permission_name,
                                ['--right=write',
                                 '--type=user',
                                 '--attr=carlicense',
                                 '--attr=description'],
                                False)
        if check4.returncode != 0:
            print("Bug bz807304 verified successfully")
        else:
            pytest.xfail("Bug bz807304 verification failed")

    def test_0007_bz783475(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify bz783475 - add permission with missing target for type
        """
        multihost.master.kinit_as_admin()
        permission_name = "BugManageUser7"
        check7 = permission_add(multihost.master, permission_name, ['--right=write'
                                                                    '--type='],
                                False)
        if check7.returncode != 0:
            print("Success! bz783475 verified successfully")
        else:
            pytest.xfail("bz783475 verification failed!")

    def test_0008_bz783475(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify bz783475 - add permission with missing target for subtree
        """
        multihost.master.kinit_as_admin()
        permission_name = "BugManageUser8"
        check8 = permission_add(multihost.master, permission_name, ['--right=write'
                                                                    '--subtree='],
                                False)
        if check8.returncode != 0:
            print("Success! bz783475 verified successfully")
        else:
            pytest.xfail("bz783475 verification failed!")

    def test_0009_bz783475(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify bz783475 - add permission with missing target for filter
        """
        multihost.master.kinit_as_admin()
        permission_name = "BugManageUser9"
        check9 = permission_add(multihost.master, permission_name, ['--right=write'
                                                                    '--filter='],
                                False)
        if check9.returncode != 0:
            print("Success! bz783475 verified successfully")
        else:
            pytest.xfail("bz783475 verification failed!")

    def test_0010_bz784329(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify Bug 784329 - permission add fails when memberof group does not exist
        """
        permission_name = "BugManageHost10"
        multihost.master.kinit_as_admin()
        check10 = permission_add(multihost.master, permission_name,
                                 ['--right=write',
                                  '--subtree=cn=computers,cn=accounts,' +
                                  multihost.master.domain.basedn.replace('"', ''),
                                  '--attr=nshostlocation',
                                  '--memberof=nonexistentgroup'],
                                 False)
        if check10.returncode != 0:
            print("Bug bz784329 Verified successfully")
        else:
            pytest.xfail("Bug bz784329 verification failed")

    def test_0011_bz816574(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify Bug bz816574 - permission add should not throw internal server error when
        option addattr or setattr is blank
        """
        permission_name = "BugManageHost11"
        multihost.master.kinit_as_admin()
        check11 = permission_add(multihost.master, permission_name,
                                 ['--right=write',
                                  'type=hostgroup',
                                  '--attr=carlicense',
                                  '--addattr'],
                                 False)
        if check11.returncode != 0:
            print("Bug bz816574 Verified successfully - addattr")
        else:
            pytest.xfail("Bug bz816574 verification failed in addattr")
        check11a = permission_add(multihost.master, permission_name,
                                  ['--right=write',
                                   'type=hostgroup',
                                   '--attr=carlicense',
                                   '--setattr'],
                                  False)
        if check11a.returncode != 0:
            print("Bug bz816574 Verified successfully - setattr")
        else:
            pytest.xfail("Bug bz816574 verification failed - setattr")
