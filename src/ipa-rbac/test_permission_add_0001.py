"""
Overview:
Test suite to verify rbac permission-add option
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.permission_utils import permission_add, permission_del


class TestPermissionAddPositive(object):
    """
    Positive testcases related to permission-add
    """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_multi_attr(self, multihost):
        """
        IDM-IPA-TC : rbac : test to add permission for type user with multiple attr
        :return:
        """
        multihost.master.kinit_as_admin()
        permission_name = "ManageUser1"
        check1 = permission_add(multihost.master, permission_name, ['--right=write',
                                                                    '--type=user',
                                                                    '--attr=carlicense',
                                                                    '--attr=description'])
        if check1.returncode == 0:
            print("Permission "+permission_name+" added successfully")
            permission_del(multihost.master, permission_name)
        else:
            pytest.xfail("Permission "+permission_name+" add failed in test_0001_multi_attr")

    def test_0002_multi_attr_multi_permissions(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add permission for type user with multiple attr and multiple permissions
        """
        multihost.master.kinit_as_admin()
        permission_name = "ManageUser2"
        check2 = permission_add(multihost.master, permission_name, ['--right=write',
                                                                    '--right=read',
                                                                    '--type=user',
                                                                    '--attr=carlicense',
                                                                    '--attr=description'])
        if check2.returncode == 0:
            print("Permission "+permission_name+" added successfully")
            permission_del(multihost.master, permission_name)
        else:
            pytest.xfail("Permission " + permission_name +
                         " add failed in test_0002_multi_attr_multi_permissions")

    def test_0003_multi_attr_multi_permissions_add_attr(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add permission for type user with multiple attr multiple permissions and add an attribute
        """
        permission_name = "ManageUser3"
        multihost.master.kinit_as_admin()
        check3 = permission_add(multihost.master, permission_name,
                                ['--addattr=description=test',
                                 '--right=read',
                                 '--right=write',
                                 '--attr=carlicense',
                                 '--attr=description',
                                 '--type=user'])
        if check3.returncode == 0:
            print("Permission " + permission_name + " added successfully")
            permission_del(multihost.master, permission_name)
        else:
            pytest.xfail("Permission " + permission_name +
                         " add failed in test_0003_multi_attr_multi_permissions_add_attr")

    def test_0004_multi_attr_multi_permissions_set_attr(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add permission for type user with multiple attr multiple permissions and set an attribute
        """
        permission_name = "ManageUser4"
        multihost.master.kinit_as_admin()
        check4 = permission_add(multihost.master, permission_name, ['--setattr=owner=cn=test',
                                                                    '--right=read',
                                                                    '--right=write',
                                                                    '--attr=carlicense',
                                                                    '--attr=description',
                                                                    '--type=user'])
        if check4.returncode == 0:
            print("Permission " + permission_name + " added successfully")
            permission_del(multihost.master, permission_name)
        else:
            pytest.xfail("Permission " + permission_name +
                         " add failed in test_0004_multi_attr_multi_permissions_set_attr")

    def test_0005_multi_attr_multi_permissions_add_set_attr(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add permission for type user with multiple attr multiple permissions and add and set multivalued attribute
        """
        permission_name = "ManageUser5"
        multihost.master.kinit_as_admin()
        check5 = permission_add(multihost.master, permission_name, ['--setattr=owner=cn=test',
                                                                    '--addattr=owner=cn=test2',
                                                                    '--right=read',
                                                                    '--right=write',
                                                                    '--attr=carlicense',
                                                                    '--attr=description',
                                                                    '--type=user'])
        if check5.returncode == 0:
            print("Permission " + permission_name + " added successfully")
            permission_del(multihost.master, permission_name)
        else:
            pytest.xfail("Permission " + permission_name +
                         " add failed in test_0005_multi_attr_multi_permissions_add_set_attr")

    def test_0006_filter_for_groups(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add permission using filter for groups
        """
        permission_name = "ManageGroup1"
        multihost.master.kinit_as_admin()
        check6 = permission_add(multihost.master, permission_name,
                                ['--attr=member',
                                 '--right=write',
                                 '--type=user',
                                 '--filter='
                                 '(&(!(objectclass=posixgroup))(objectclass=ipausergroup))'])
        if check6.returncode == 0:
            print("Permission " + permission_name + " added successfully")
            permission_del(multihost.master, permission_name)
        else:
            pytest.xfail("Permission " + permission_name +
                         " add failed in test_0006_filter_for_groups")

    def test_0007_subtree_for_hosts(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add permission using subtree for hosts
        """
        permission_name = "ManageHost1"
        multihost.master.kinit_as_admin()
        check7 = permission_add(multihost.master, permission_name,
                                ['--right=write',
                                 '--subtree=cn=computers,cn=accounts,'
                                 + multihost.master.domain.basedn.replace('"', ''),
                                 '--memberof=groupone',
                                 '--attr=nshostlocation'])
        if check7.returncode == 0:
            print("Permission " + permission_name + " added successfully")
            permission_del(multihost.master, permission_name)
        else:
            pytest.xfail("Permission " + permission_name +
                         " add failed in test_0007_subtree_for_hosts")

    def test_0008_targetgroup(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add permission using targetgroup
        """
        permission_name = "ManageGroup2"
        multihost.master.kinit_as_admin()
        check8 = permission_add(multihost.master, permission_name,
                                ['--right=write',
                                 '--targetgroup=groupone',
                                 '--attr=description'])
        if check8.returncode == 0:
            print("Permission " + permission_name + " added successfully")
            permission_del(multihost.master, permission_name)
        else:
            pytest.xfail("Permission " + permission_name +
                         " add failed in test_0008_targetgroup")

    def test_0009_type_netgroup_multiple_attr(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add permission for type netgroup with multiple attr
        """
        permission_name = "ManageNetgroup1"
        multihost.master.kinit_as_admin()
        check9 = permission_add(multihost.master, permission_name,
                                ['--right=all',
                                 '--filter=(objectclass=nisNetgroup)',
                                 '--attr=memberNisNetgroup',
                                 '--attr=nisNetgroupTriple',
                                 '--attr=description'])
        if check9.returncode == 0:
            print("Permission " + permission_name + " added successfully")
            permission_del(multihost.master, permission_name)
        else:
            pytest.xfail("Permission " + permission_name +
                         " add failed in test_0009_type_netgroup_multiple_attr")

    def test_0010_dnsrecord_multiple_attr(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add permission for type dnsrecord with multiple attr
        """
        permission_name = "ManageDNSRecord1"
        multihost.master.kinit_as_admin()
        check10 = permission_add(multihost.master, permission_name,
                                 ['--right=write',
                                  '--subtree=idnsname='+multihost.master.domain.name +
                                  '.,cn=dns,' + multihost.master.domain.basedn.replace('"', ''),
                                  '--memberof=groupone',
                                  '--attr=nshostlocation'])
        if check10.returncode == 0:
            print("Permission " + permission_name + " added successfully")
            permission_del(multihost.master, permission_name)
        else:
            pytest.xfail("Permission " + permission_name +
                         " add failed in test_0010_dnsrecord_multiple_attr")

    def class_teardown(self, multihost):
        """ Full suite teardown """
        pass
