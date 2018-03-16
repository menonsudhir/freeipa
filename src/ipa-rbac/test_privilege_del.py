"""
Overview:
Test suite to verify rbac privilege-del option
"""

from __future__ import print_function
import pytest
from ipa_pytests.shared.privilege_utils import privilege_del
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import


class TestPrivilegeDel(object):
    """
    Testcases related to privilege-del
    """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_non_existent_privilege(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to delete privilege with option continue
        """
        privilege_name = "Non Existent Privilege"
        expmsg = "Failed to remove: " + privilege_name
        check1 = privilege_del(multihost.master, privilege_name,
                               ['--continue'],
                               False)
        if expmsg not in check1.stdout_text:
            print(check1.stderr_text)
            print(check1.stdout_text)
            pytest.fail("Deleting non existent privilege should have failed")
