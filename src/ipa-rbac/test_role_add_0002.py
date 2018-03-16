"""
Overview:
Test suite to verify rbac role-add option
"""
from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.role_utils import role_add, role_del


class TestRoleAddNegative(object):
    """
    Negative testcases related to role-add
    """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_invalid_setattr(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative Test to add role with invalid setattr
        """
        role_name = "Hostgroup Admin with invalid seeAlso"
        role_desc = "--desc=Hostgroup Admin with invalid seeAlso"
        attr = "--setattr=xyz=XYZ"
        check1 = role_add(multihost.master, role_name, [role_desc,
                                                        attr], False)
        expmsg = 'ipa: ERROR: attribute \"xyz\" not allowed'
        if expmsg not in check1.stderr_text:
            pytest.fail("invalid attr set should have failed")

    def test_0002_invalid_addattr(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative Test to add role with invalid addattr
        """
        role_name = "Hostgroup Admin with invalid seeAlso"
        role_desc = "--desc=Hostgroup Admin with invalid seeAlso"
        attr = "--addattr=xyz=XYZ"
        check2 = role_add(multihost.master, role_name, [role_desc,
                                                        attr], False)
        expmsg = 'ipa: ERROR: attribute \"xyz\" not allowed'
        if expmsg not in check2.stderr_text:
            pytest.fail("invalid attr set should have failed")

    def test_0003_missing_name(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to add role with missing name
        """
        role_name = ""
        role_desc = "--desc=Host Admin"
        check3 = role_add(multihost.master, role_name, [role_desc], False)
        expmsg = "ipa: ERROR: 'name' is required"
        if expmsg not in check3.stderr_text:
            pytest.fail("missing name role add should have failed")

    def test_0004_duplicate_role(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to add duplicate role
        """
        role_name = "Host Admin"
        role_desc = "--desc=Host Admin"
        role_add(multihost.master, role_name, [role_desc])
        check4 = role_add(multihost.master, role_name, [role_desc], False)
        expmsg = "ipa: ERROR: role with name \"" + role_name + "\" already exists"
        role_del(multihost.master, role_name)
        if expmsg not in check4.stderr_text:
            pytest.fail("duplicate role add should have failed")

    def test_0005_blank_desc(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add role with blank desc
        """
        role_name = "Add User with blank desc"
        role_desc = "--desc"
        check5 = role_add(multihost.master, role_name, [role_desc], False)
        expmsg = "ipa: error: --desc option requires an argument"
        if expmsg not in check5.stderr_text:
            pytest.fail("Privilege add with blank desc should have failed")

    def test_0006_blank_setattr(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add role with blank setattr
        """
        role_name = "Hostgroup Admin with blank seeAlso"
        role_desc = "--desc=Hostgroup Admin with blank seeAlso"
        attr = "--setattr"
        expmsg = 'ipa: error: --setattr option requires an argument'
        check6 = role_add(multihost.master, role_name,
                          [role_desc,
                           attr], False)
        if expmsg not in check6.stderr_text:
            pytest.fail("Privilege add with blank setattr should have failed")
