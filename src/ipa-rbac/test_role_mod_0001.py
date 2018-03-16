"""
Overview:
Test suite to verify rbac role-mod option
"""

from __future__ import print_function
from ipa_pytests.shared.role_utils import role_mod
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import


class TestRoleModPositive(object):
    """
    Positive testcases related to role-mod
    """

    role_name = "helpdesk"

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_desc(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to mod desc of role
        """
        new_role_desc = "Helpdesk Updated"
        attr = "--desc=" + new_role_desc
        role_mod(multihost.master, self.role_name,
                 [attr])

    def test_0002_rename_role(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to rename role
        """
        new_role_name = "helpdesk Updated"
        attr = "--rename"
        role_mod(multihost.master, self.role_name,
                 [attr + "=" + new_role_name])

    def test_0003_use_setattr(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to rename role using setattr
        """
        role_name = "helpdesk Updated"
        attr = "--setattr=cn=" + self.role_name
        role_mod(multihost.master, role_name,
                 [attr])

    def test_0004_use_addattr(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to mod role to use addattr
        """
        attr1 = "--addattr"
        add_owner1 = "seeAlso=cn=HostgroupCLI"
        attr2 = "--addattr"
        add_owner2 = "seeAlso=cn=HostCLI"
        role_mod(multihost.master, self.role_name,
                 [attr1 + "=" + add_owner1,
                  attr2 + "=" + add_owner2])

    def test_0005_delattr(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to mod role to delattr with option rights
        """
        role_desc = "seeAlso=cn=HostCLI"
        attr = "--delattr=" + role_desc
        role_mod(multihost.master, self.role_name,
                 [attr, '--rights'])

    def test_cleanup(self, multihost):
        """
        Cleanup changes made
        :param multihost:
        :return:
        """
        attr1 = "--desc"
        role_desc = "Helpdesk"
        attr2 = "--delattr"
        del_owner = "seeAlso=cn=HostgroupCLI"
        role_mod(multihost.master, self.role_name,
                 [attr1 + "=" + role_desc,
                  attr2 + "=" + del_owner])
