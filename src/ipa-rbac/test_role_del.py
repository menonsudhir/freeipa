"""
Overview:
Test suite to verify rbac role-del option
"""

from __future__ import print_function
import pytest
from ipa_pytests.shared.role_utils import role_del
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import


class TestRoleDel(object):
    """
    Testcases related to role-del
    """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_non_existent_role(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to delete role with option continue
        """
        role_name = "Non Existent Role"
        expmsg = "Failed to remove: " + role_name
        check1 = role_del(multihost.master, role_name,
                          ['--continue'],
                          False)
        if expmsg not in check1.stdout_text:
            print(check1.stderr_text)
            print(check1.stdout_text)
            pytest.fail("Deleting non existent role should have failed")
