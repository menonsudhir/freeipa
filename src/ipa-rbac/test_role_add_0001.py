"""
Overview:
Test suite to verify rbac role-add option
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.role_utils import role_add, role_del


class TestRoleAddPositive(object):
    """
    Positive testcases related to role-add
    """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_add_role(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add role
        """
        role_name = "Add Admin"
        role_desc = "--desc=Add Admin"
        role_add(multihost.master, role_name, [role_desc])
        role_del(multihost.master, role_name)

    def test_0002_raw(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add role with option raw
        """
        role_name = "Hostgroup Admin"
        role_desc = "--desc=Hostgroup Admin"
        check2 = role_add(multihost.master, role_name,
                          [role_desc,
                           '--all',
                           '--raw'])
        check2 = check2.stdout_text.split("\n")
        objectclass_occurences = 0
        for line in check2:
            if "objectClass:" in line:
                objectclass_occurences += 1
        role_del(multihost.master, role_name)
        if objectclass_occurences != 3:
            pytest.fail("Did not find expected objectclass for "+role_name)

    def test_0003_all(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add role with option all
        """
        role_name = "Netgroup Admin"
        role_desc = "--desc=Netgroup Admin"
        check3 = role_add(multihost.master, role_name,
                          [role_desc,
                           '--all'])
        check3 = check3.stdout_text.split("\n")
        objectclass_occurences = 0
        for line in check3:
            if "objectclass:" in line:
                objectclass_occurences += 1
        role_del(multihost.master, role_name)
        if objectclass_occurences != 1:
            pytest.fail("Did not find expected objectclass for "+role_name +
                        "object occurrences=" + str(objectclass_occurences))

    def test_0004_comma(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add role with comma
        """
        role_name = "Hostgroup, Netgroup - Admin"
        role_desc = "--desc=Hostgroup, Netgroup - Admin"
        role_add(multihost.master, role_name, [role_desc])
        role_del(multihost.master, role_name)

    def test_0005_setattr(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add role with setattr
        """
        role_name = "Hostgroup Admin with see"
        role_desc = "--desc=Hostgroup Admin with seeAlso"
        attr = "--setattr=seeAlso=cn=HostgroupCLI"
        role_add(multihost.master, role_name,
                 [role_desc,
                  attr])
        role_del(multihost.master, role_name)

    def test_0006_addattr(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add role with addattr
        """
        role_name = "Hostgroup Admin with multiple seeAlso"
        role_desc = "--desc=Hostgroup Admin with multiple seeAlso"
        attr = "--addattr=seeAlso=cn=HostgroupCLI --addattr=seeAlso=cn=HostCLI"
        role_add(multihost.master, role_name,
                 [role_desc,
                  attr])
        role_del(multihost.master, role_name)
