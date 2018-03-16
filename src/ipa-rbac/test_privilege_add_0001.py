"""
Overview:
Test suite to verify rbac privilege-add option
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.privilege_utils import privilege_add
from ipa_pytests.shared.privilege_utils import privilege_del


class TestPrivilegeAddPositive(object):
    """
    Positive testcases related to privilege-add
    """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_add_privilege(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add privilege
        """
        privilege_name = "Add User"
        privilege_desc = "--desc=Add User"
        privilege_add(multihost.master, privilege_name, [privilege_desc])
        privilege_del(multihost.master, privilege_name)

    def test_0002_comma(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add privilege with comma
        """
        privilege_name = "Add User, Group"
        privilege_desc = "--desc=Add User, Group"
        privilege_add(multihost.master, privilege_name, [privilege_desc])
        privilege_del(multihost.master, privilege_name)

    def test_0003_setattr(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add privilege with setattr
        """
        privilege_name = "Add User with owner"
        privilege_desc = "--desc=Add User with owner"
        attr = "--setattr=owner=cn=ABC"
        privilege_add(multihost.master, privilege_name,
                      [privilege_desc,
                       attr])
        privilege_del(multihost.master, privilege_name)

    def test_0004_addattr(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add privilege with addattr
        """
        privilege_name = "Add User with multiple owner"
        privilege_desc = "--desc=Add User with multiple owner"
        attr = "--addattr=owner=cn=XYZ --addattr=owner=cn=ZZZ"
        privilege_add(multihost.master, privilege_name,
                      [privilege_desc,
                       attr])
        privilege_del(multihost.master, privilege_name)

    def test_0005_raw(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add privilege with option raw
        """
        privilege_name = "Modify User"
        privilege_desc = "--desc=Modify User"
        check5 = privilege_add(multihost.master, privilege_name,
                               [privilege_desc,
                                '--all',
                                '--raw'])
        check5a = check5.stdout_text.split("\n")
        objectclass_occurences = 0
        for line in check5a:
            if "objectClass:" in line:
                objectclass_occurences += 1
        if objectclass_occurences != 3:
            pytest.fail("Did not find expected objectclass for "+privilege_name)
        privilege_del(multihost.master, privilege_name)

    def test_0006_all(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add  privilege with option all
        """
        privilege_name = "Modify Groups"
        privilege_desc = "--desc=Modify Groups"
        check6 = privilege_add(multihost.master, privilege_name,
                               [privilege_desc,
                                '--all'])
        check6a = check6.stdout_text.split("\n")
        objectclass_occurences = 0
        for line in check6a:
            if "objectclass:" in line:
                objectclass_occurences += 1
        if objectclass_occurences != 1:
            privilege_del(multihost.master, privilege_name)
            print(check6.stdout_text)
            pytest.fail("Did not find expected objectclass for "+privilege_name +
                        "object occurences=" + str(objectclass_occurences))
        privilege_del(multihost.master, privilege_name)

    def test_0007_blank_desc(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add privilege with blank desc
        """
        privilege_name = "Add User with blank desc"
        privilege_desc = "--desc="
        privilege_add(multihost.master, privilege_name, [privilege_desc])
        privilege_del(multihost.master, privilege_name)
