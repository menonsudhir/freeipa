"""
Test suite to verify permission-find option
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.permission_utils import permission_del, permission_find, permission_add


class TestPermissionFindPositive(object):
    """
    Positive testcases related to permission-find
    """
    def test_0001_find_right(self, multihost):
        """
        IDM-IPA-TC : rbac : Function to find permission with option right
        """
        permission_name = "ManageFind1"
        multihost.master.kinit_as_admin()
        right = 'all'
        check1 = permission_add(multihost.master, permission_name,
                                ['--right=' + right,
                                 '--filter=(objectclass=nisNetgroup)',
                                 '--attr=memberNisNetgroup',
                                 '--attr=nisNetgroupTriple',
                                 '--attr=description'])
        if check1.returncode == 0:
            check1a = permission_find(multihost.master, permission_name=None,
                                      options_list=['--right=' + right,
                                                    '--all'])
            if permission_name in check1a.stdout_text:
                print("permissions with option right=" + right + " found correctly")
            else:
                pytest.xfail("Something wrong in finding permissions with option right="
                             + right)
            permission_del(multihost.master, permission_name)

    def test_0002_find_attrs(self, multihost):
        """
        IDM-IPA-TC : rbac : Function to find permission with option attrs
        """
        permission_name1 = "Manage Host Keytab"
        permission_name2 = "Manage Service Keytab"
        multihost.master.kinit_as_admin()
        check2 = permission_find(multihost.master, permission_name=None,
                                 options_list=['--attrs=krbprincipalkey',
                                               '--attrs=krblastpwdchange',
                                               '--all'])
        if permission_name1 in check2.stdout_text and permission_name2 in check2.stdout_text:
            print("permission-find with option attrs test successful")
        else:
            pytest.xfail(permission_name1 + " or " + permission_name2
                         + " not found using permission-find with appropriate attrs")

    def test_0003_find_type(self, multihost):
        """
        IDM-IPA-TC : rbac : Function to findpermission with option type
        """
        permission_name = "ManageFind3"
        multihost.master.kinit_as_admin()
        permission_add(multihost.master, permission_name,
                       ['--right=write',
                        '--attr=arecord',
                        '--type=dnsrecord'])
        check3a = permission_find(multihost.master, permission_name=None,
                                  options_list=['--type=dnsrecord',
                                                '--all'])
        if permission_name in check3a.stdout_text:
            print("Permission-find with option type test successful")
        else:
            pytest.xfail(permission_name+" not found")
        permission_del(multihost.master, permission_name)

    def test_0004_find_memberof(self, multihost):
        """
        IDM-IPA-TC : rbac : Function to find permission with option memberof
        """
        multihost.master.kinit_as_admin()
        permission_name = "ManageFind4"
        permission_add(multihost.master, permission_name,
                       ['--right=write',
                        '--subtree=cn=computers,cn=accounts,'
                        + multihost.master.domain.basedn.replace('"', ''),
                        '--memberof=groupone',
                        '--attr=nshostlocation'])
        check4a = permission_find(multihost.master, permission_name=None,
                                  options_list=['--memberof=groupone',
                                                '--all'])
        if permission_name in check4a.stdout_text:
            print("permission-find with option memberof test successful")
        else:
            pytest.xfail(permission_name+" not found")
        permission_del(multihost.master, permission_name)

    def test_0005_find_filer(self, multihost):
        """
        IDM-IPA-TC : rbac : Function to find permission with option filter
        """
        multihost.master.kinit_as_admin()
        permission_name = "ManageFind5"
        permission_add(multihost.master, permission_name,
                       ['--attr=member',
                        '--right=write',
                        '--type=user',
                        '--filter=(&(!(objectclass=posixgroup))(objectclass=ipausergroup))'])
        check5a = permission_find(multihost.master, permission_name=None, options_list=[
            '--filter=(&(!(objectclass=posixgroup))(objectclass=ipausergroup))',
            '--all'])
        if permission_name in check5a.stdout_text:
            print("permission-find with option filter test successful")
        else:
            pytest.xfail(permission_name + " not found")
        permission_del(multihost.master, permission_name)

    def test_0006_multi_attr(self, multihost):
        """
        IDM-IPA-TC : rbac : Function to find permission with options attrs permissions type
        """
        multihost.master.kinit_as_admin()
        permission61 = "FindManageUser61"
        permission_add(multihost.master, permission61, ['--right=write',
                                                        '--type=user',
                                                        '--attr=carlicense',
                                                        '--attr=description'])
        permission62 = "FindManageUser62"
        permission_add(multihost.master, permission62, ['--right=write',
                                                        '--right=read',
                                                        '--type=user',
                                                        '--attr=carlicense',
                                                        '--attr=description'])
        permission63 = "FindManageUser63"
        permission_add(multihost.master, permission63, ['--addattr=description=test',
                                                        '--right=read',
                                                        '--right=write',
                                                        '--attr=carlicense',
                                                        '--attr=description',
                                                        '--type=user'])
        permission64 = "FindManageUser64"
        permission_add(multihost.master, permission64, ['--setattr=owner=cn=test',
                                                        '--right=read',
                                                        '--right=write',
                                                        '--attr=carlicense',
                                                        '--attr=description',
                                                        '--type=user'])
        permission65 = "FindManageUser65"
        permission_add(multihost.master, permission65, ['--setattr=owner=cn=test',
                                                        '--addattr=owner=cn=test2',
                                                        '--right=read',
                                                        '--right=write',
                                                        '--attr=carlicense',
                                                        '--attr=description',
                                                        '--type=user'])
        permission66 = "Modify Users"
        check6a = permission_find(multihost.master, permission_name=None,
                                  options_list=['--attrs=description',
                                                '--right=write',
                                                '--type=user',
                                                '--all'])
        perm_array = [permission61,
                      permission62,
                      permission63,
                      permission64,
                      permission65,
                      permission66]
        for permission in perm_array:
            if permission not in check6a.stdout_text:
                pytest.fail("Error in permission-find with options attrs permissions type")
        print("permission-find with options attrs permissions type test successful")
        permission_del(multihost.master, permission61, [permission62,
                                                        permission63,
                                                        permission64,
                                                        permission65,
                                                        '--continue'])

    def test_0007_find_pkey_only(self, multihost):
        """
        IDM-IPA-TC : rbac : Function to find permission with option pkey only test of ipa permission
        """
        multihost.master.kinit_as_admin()
        check7 = permission_find(multihost.master, permission_name=None,
                                 options_list=['--pkey-only', '--all'])
        if "Remove Hosts" in check7.stdout_text and "Remove Users" in check7.stdout_text:
            print("find permission with option pkey only test of ipa permission verified")

    def test_0008_find_all_raw(self, multihost):
        """
        IDM-IPA-TC : rbac : Function to verify permission attrs after a find with option all
        """
        permission_name = "FindManageHost"
        multihost.master.kinit_as_admin()
        permission_add(multihost.master, permission_name,
                       ['--right=write',
                        '--subtree=cn=computers,cn=accounts,'
                        + multihost.master.domain.basedn.replace('"', ''),
                        '--memberof=groupone',
                        '--attr=nshostlocation'])
        check8a = permission_find(multihost.master, permission_name=None,
                                  options_list=['--memberof=groupone', '--all'])
        if permission_name in check8a.stdout_text:
            print("Verified bz785259 permissions are found for " + permission_name)
        else:
            pytest.xfail("Error in verification of bz785259")
        permission_del(multihost.master, permission_name)
