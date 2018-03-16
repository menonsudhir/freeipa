"""
Overview:
Test suite to verify rbac privilege-add option
"""
from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.privilege_utils import privilege_add, privilege_del


class TestPrivilegeAddNegative(object):
    """
    Negative testcases related to permission-add
    """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_invalid_setattr(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative Test to add privilege with invalid setattr
        """
        privilege_name = "Add User with invalid attr"
        privilege_desc = "--desc=Add User with invalid attr"
        attr = "--setattr=xyz=XYZ"
        check1 = privilege_add(multihost.master, privilege_name, [privilege_desc,
                                                                  attr], False)
        expmsg = 'ipa: ERROR: attribute \"xyz\" not allowed'
        if expmsg not in check1.stderr_text:
            pytest.fail("invalid attr set should have failed")

    def test_0002_invalid_addattr(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative Test to add privilege with invalid addattr
        """
        privilege_name = "Add User with invalid attr"
        privilege_desc = "--desc=Add User with invalid attr"
        attr = "--addattr=xyz=XYZ"
        check2 = privilege_add(multihost.master, privilege_name, [privilege_desc,
                                                                  attr], False)
        expmsg = 'ipa: ERROR: attribute \"xyz\" not allowed'
        if expmsg not in check2.stderr_text:
            pytest.fail("invalid attr set should have failed")

    def test_0004_duplicate_privilege(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to add duplicate privilege
        """
        privilege_name = "Add User"
        privilege_desc = "--desc=Add User"
        privilege_add(multihost.master, privilege_name, [privilege_desc])
        check4 = privilege_add(multihost.master, privilege_name, [privilege_desc], False)
        expmsg = "ipa: ERROR: privilege with name \"" + privilege_name + "\" already exists"
        if expmsg not in check4.stderr_text:
            pytest.fail("duplicate privilege add should have failed")
        privilege_del(multihost.master, privilege_name)
