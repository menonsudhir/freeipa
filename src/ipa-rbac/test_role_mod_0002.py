"""
Overview:
Test suite to verify rbac role-mod option
"""

from __future__ import print_function
from ipa_pytests.shared.role_utils import role_mod
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
import pytest


class TestRoleModNegative(object):
    """
    Negative testcases related to role-mod
    """

    role_name = "helpdesk"

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_multiple_addattr(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to mod role to addattr multiple attr when only one one value is allowed
        """
        attr = "--addattr"
        add_description = "description=AnotherDescriptionNotAllowed"
        check1 = role_mod(multihost.master, self.role_name,
                          [attr+"="+add_description],
                          False)
        expmsg = "ipa: ERROR: description: Only one value allowed."
        if expmsg not in check1.stderr_text:
            pytest.fail("Addition extra description attr should have failed")

    def test_0002_addattr_invalid_syn(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to mod role to addattr with invalid syntax
        """
        attr = "--addattr"
        add_owner = "owner=xyz"
        check2 = role_mod(multihost.master, self.role_name,
                          [attr + "=" + add_owner],
                          False)
        expmsg = "ipa: ERROR: owner: value #0 invalid per syntax: Invalid syntax."
        if expmsg not in check2.stderr_text:
            pytest.fail("Modification of the role should have failed")

    def test_0003_blank_desc(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to mod role to use blank desc
        """
        attr = "--desc"
        check3 = role_mod(multihost.master, self.role_name,
                          [attr], False)
        expmsg = "ipa: error: --desc option requires 1 argument"
        if expmsg not in check3.stderr_text:
            print(check3.stderr_text)
            pytest.fail("role mod with blank decription should have failed")

    def test_0004_blank_rename(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to mod role to use blank rename
        """
        attr = "--rename="
        expmsg = "ipa: ERROR: invalid 'rename': can't be empty"
        check4 = role_mod(multihost.master, self.role_name,
                          [attr],
                          False)
        if expmsg not in check4.stderr_text:
            print(check4.stderr_text)
            pytest.fail("Modification of the role should have failed")

    def test_0005_same_rename(self, multihost):
        """
        IDM-IPA-TC : rbac : Negative test to mod role to rename to same name
        """
        attr = "--rename"
        expmsg = "ipa: ERROR: no modifications to be performed"
        check5 = role_mod(multihost.master, self.role_name,
                          [attr+"="+self.role_name],
                          False)
        if expmsg not in check5.stderr_text:
            pytest.fail("Modification of the role should have failed")
