"""
Overview:
Test suite to verify rbac privilege-mod option
"""

from __future__ import print_function
from ipa_pytests.shared.privilege_utils import privilege_mod
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import


class TestPrivilegeModPositive(object):
    """
    Positive testcases related to privilege-mod
    """

    privilege_name = "Netgroups Administrators"

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_desc(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to mod desc of privilege
        """
        new_privilege_desc = "NetgroupsAdmin"
        attr = "--desc=" + new_privilege_desc
        privilege_mod(multihost.master, self.privilege_name,
                      [attr])

    def test_0002_rename_privilege(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to rename privilege
        """
        new_privilege_name = "NetgroupsAdmin"
        attr = "--rename"
        privilege_mod(multihost.master, self.privilege_name,
                      [attr + "=" + new_privilege_name])

    def test_0003_use_addattr(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to mod privilege to use addattr
        """
        privilege_name = "NetgroupsAdmin"
        attr1 = "--addattr"
        add_owner1 = "owner=cn=abc"
        attr2 = "--addattr"
        add_owner2 = "owner=cn=def"
        privilege_mod(multihost.master, privilege_name,
                      [attr1 + "=" + add_owner1,
                       attr2 + "=" + add_owner2])

    def test_0004_delattr(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to mod privilege to delattr
        """
        privilege_name = "NetgroupsAdmin"
        privilege_desc = "description=NetgroupsAdmin"
        attr = "--delattr=" + privilege_desc
        privilege_mod(multihost.master, privilege_name,
                      [attr])

    def test_0005_blank_desc(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to mod privilege to use blank desc
        """
        attr1 = "--desc"
        privilege_desc = "Netgroups Administrators"
        privilege_mod(multihost.master, "NetgroupsAdmin",
                      [attr1 + "=" + privilege_desc, ])
        attr = "--desc="
        privilege_name = "NetgroupsAdmin"
        check5 = privilege_mod(multihost.master, privilege_name,
                               [attr])
        privilege_desc = "--desc=NetgroupsAdmin"
        privilege_mod(multihost.master, privilege_name,
                      [privilege_desc])
        if "Description" in check5.stdout_text:
            pytest.fail("Blank decription should equal removal of description")

    def test_cleanup(self, multihost):
        """
        Cleanup changes made
        :param multihost:
        :return:
        """
        attr1 = "--desc"
        privilege_desc = "Netgroups Administrators"
        attr2 = "--delattr"
        del_owner1 = "owner=cn=abc"
        attr3 = "--delattr"
        del_owner2 = "owner=cn=def"
        privilege_mod(multihost.master, "NetgroupsAdmin",
                      [attr1 + "=" + privilege_desc,
                       attr2 + "=" + del_owner1,
                       attr3 + "=" + del_owner2,
                       '--rename=' + self.privilege_name])
