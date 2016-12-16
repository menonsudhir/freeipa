"""
Overview:
Test suite to verify rbac privilege-mod option
"""

from __future__ import print_function
from ipa_pytests.shared.privilege_utils import privilege_mod
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
import pytest


class TestPrivilegeModNegative(object):
    """
    Negative testcases related to privilege-mod
    """

    privilege_name = "Netgroups Administrators"

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_multiple_addattr(self, multihost):
        """
        Test to mod privilege to addattr multiple attr when only one one value is allowed
        :param multihost:
        :return:
        """
        attr = "--addattr"
        add_description = "description=AnotherDescriptionNotAllowed"
        check1 = privilege_mod(multihost.master, self.privilege_name,
                               [attr+"="+add_description],
                               False)
        expmsg = "ipa: ERROR: description: Only one value allowed."
        if expmsg not in check1.stderr_text:
            pytest.fail("Addition extra description attr should have failed")

    def test_0002_addattr_invalid_syn(self, multihost):
        """
        Test to mod privilege to addattr with invalid syntax
        :param multihost:
        :return:
        """
        attr = "--addattr"
        add_owner = "owner=xyz"
        check2 = privilege_mod(multihost.master, self.privilege_name,
                               [attr + "=" + add_owner],
                               False)
        expmsg = "ipa: ERROR: owner: value #0 invalid per syntax: Invalid syntax."
        if expmsg not in check2.stderr_text:
            pytest.fail("Modification of the privilege should have failed")

    def test_0004_blank_rename(self, multihost):
        """
        Test to mod privilege to use blank rename
        :param multihost:
        :return:
        """
        attr = "--rename="
        expmsg = "ipa: ERROR: invalid 'rename': can't be empty"
        check4 = privilege_mod(multihost.master, self.privilege_name,
                               [attr],
                               False)
        if expmsg not in check4.stderr_text:
            print(check4.stderr_text)
            pytest.fail("Modification of the privilege should have failed")

    def test_0005_same_rename(self, multihost):
        """
        Test to mod privilege to rename to same name
        :param multihost:
        :return:
        """
        attr = "--rename"
        expmsg = "ipa: ERROR: no modifications to be performed"
        check5 = privilege_mod(multihost.master, self.privilege_name,
                               [attr+"="+self.privilege_name],
                               False)
        if expmsg not in check5.stderr_text:
            pytest.fail("Modification of the privilege should have failed")
