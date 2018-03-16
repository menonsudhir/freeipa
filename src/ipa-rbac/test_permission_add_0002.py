"""
Overview:
Test suite to verify rbac permission-add option
"""
from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.permission_utils import permission_add


class TestPermissionAddNegative(object):
    """
    Negative testcases related to permission-add
    """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_invalid_right(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative Test to add permission with invalid right
        """
        multihost.master.kinit_as_admin()
        permission_name = "ManageUser1"
        check1 = permission_add(multihost.master, permission_name, ['--right=reads'
                                                                    '--type=user',
                                                                    '--attr=carlicense',
                                                                    '--attr=description'],
                                False)
        if check1.returncode != 0:
            print("Success! permission-add with invalid right failed")
        else:
            pytest.xfail("This test should have failed!")

    def test_0002_missing_right(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative Test to add permission with missing right
        """
        multihost.master.kinit_as_admin()
        permission_name = "ManageUser2"
        check2 = permission_add(multihost.master, permission_name, ['--right='
                                                                    '--type=user',
                                                                    '--attr=carlicense',
                                                                    '--attr=description'],
                                False)
        if check2.returncode != 0:
            print("Success! permission-add with missing right failed")
        else:
            pytest.xfail("This test should have failed!")

    def test_0003_invalid_attr(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative Test to add permission with invalid attr
        """
        multihost.master.kinit_as_admin()
        permission_name = "ManageUser3"
        check2 = permission_add(multihost.master, permission_name, ['--right=read'
                                                                    '--type=user',
                                                                    '--attr=invalidattr'],
                                False)
        if check2.returncode != 0:
            print("Success! permission-add with invalid attr failed")
        else:
            pytest.xfail("This test should have failed!")

    def test_0004_multiple_targets_subtree(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative Test to add permission with multiple targets type and subtree
        """
        multihost.master.kinit_as_admin()
        permission_name = "ManageUser4"
        check4 = permission_add(multihost.master, permission_name,
                                ['--right=read'
                                 '--type=user',
                                 '--attr=carlicense',
                                 '--subtree=cn=users,cn=accounts,' +
                                 multihost.master.domain.basedn.replace('"', '')],
                                False)
        if check4.returncode != 0:
            print("Success! permission-add with multiple targets type and subtree failed")
        else:
            pytest.xfail("This test should have failed!")

    def test_0005_multiple_targets_filter(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative Test to add permission with multiple targets type and filter
        """
        multihost.master.kinit_as_admin()
        permission_name = "ManageUser5"
        check5 = permission_add(multihost.master, permission_name,
                                ['--right=read'
                                 '--type=user',
                                 '--attr=carlicense',
                                 '--filter=(givenname=xyz)'],
                                False)
        if check5.returncode != 0:
            print("Success! permission-add with multiple targets type and filter failed")
        else:
            pytest.xfail("This test should have failed!")

    def test_0006_missing_target_type(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative Test to add permission with missing target for type
        """
        multihost.master.kinit_as_admin()
        permission_name = "ManageUser6"
        check6 = permission_add(multihost.master, permission_name, ['--right=write'
                                                                    '--type'],
                                False)
        if check6.returncode != 0:
            print("Success! permission-add with missing target for type failed")
        else:
            pytest.xfail("This test should have failed!")

    def test_0007_missing_target_subtree(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative Test to add permission with missing target for subtree
        """
        multihost.master.kinit_as_admin()
        permission_name = "ManageUser7"
        check7 = permission_add(multihost.master, permission_name, ['--right=write'
                                                                    '--subtree'],
                                False)
        if check7.returncode != 0:
            print("Success! permission-add with missing target for subtree failed")
        else:
            pytest.xfail("This test should have failed!")

    def test_0008_missing_target_filter(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative Test to add permission with missing target for filter
        """
        multihost.master.kinit_as_admin()
        permission_name = "ManageUser8"
        check8 = permission_add(multihost.master, permission_name, ['--right=write'
                                                                    '--filter'],
                                False)
        if check8.returncode != 0:
            print("Success! permission-add with missing target for filter failed")
        else:
            pytest.xfail("This test should have failed!")

    def test_0009_missing_memberof(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative Test to add permission using missing memberof group
        """
        permission_name = "ManageHost9"
        multihost.master.kinit_as_admin()
        check9 = permission_add(multihost.master, permission_name,
                                ['--right=write',
                                 '--subtree=cn=computers,cn=accounts,'
                                 + multihost.master.domain.basedn.replace('"', ''),
                                 '--attr=nshostlocation',
                                 '--memberof'],
                                False)
        if check9.returncode != 0:
            print("Success! add permission using missing memberof group failed")
        else:
            pytest.xfail("This test should have failed")

    def test_0010_invalid_type(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to add permission using invalid type
        """
        permission_name = 'NegManageGroup10'
        multihost.master.kinit_as_admin()
        check10 = permission_add(multihost.master, permission_name,
                                 ['--right=write',
                                  '--type=xyz'], False)
        if check10.returncode != 0:
            print("Success! add permission using invalid type failed")
        else:
            pytest.xfail("This test should have failed")

    def test_0011_invalid_filter(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to add permission using invalid filter
        """
        permission_name = 'NegManageGroup11'
        multihost.master.kinit_as_admin()
        check11 = permission_add(multihost.master, permission_name,
                                 ['--right=write',
                                  '--filter=(&(!(objectclass))(objectclass=ipausergroup))'],
                                 False)
        if check11.returncode != 0:
            print("Success! add permission using invalid filter failed")
        else:
            pytest.xfail("This test should have failed")

    def test_0012_invalid_subtree(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to add permission using invalid subtree
        """
        permission_name = 'NegManageGroup12'
        multihost.master.kinit_as_admin()
        check12 = permission_add(multihost.master, permission_name,
                                 ['--right=write',
                                  '--subtree=xyz'], False)
        if check12.returncode != 0:
            print("Success! add permission using invalid subtree failed")
        else:
            pytest.xfail("This test should have failed")

    def test_0013_invalid_addattr_setattr(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to add permission using invalid addattr/setattr
        """
        permission_name = 'NegManageGroup13'
        multihost.master.kinit_as_admin()
        check13 = permission_add(multihost.master, permission_name,
                                 ['--right=write',
                                  'type=hostgroup',
                                  '--attr=carlicense',
                                  '--addattr=xyz=test'],
                                 False)
        if check13.returncode != 0:
            print("Success! add permission using invalid addattr failed")
        else:
            pytest.xfail("This test permission-add using invalid addattr should have failed")

        permission_name = 'NegManageGroup13a'
        multihost.master.kinit_as_admin()
        check13a = permission_add(multihost.master, permission_name,
                                  ['--right=write',
                                   'type=hostgroup',
                                   '--attr=carlicense',
                                   '--setattr=owner=test'],
                                  False)
        if check13a.returncode != 0:
            print("Success! add permission using invalid setattr failed")
        else:
            pytest.xfail("This test permission-add using invalid setattr should have failed")
