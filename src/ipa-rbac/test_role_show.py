"""
Overview:
Test suite to verify rbac role-show option
"""

from __future__ import print_function
import pytest
from ipa_pytests.shared.role_utils import role_show
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import


class TestRoleShow(object):
    """
    Testcases related to role-show
    """
    role_name = "helpdesk"

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_rights(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to show role with option rights
        """
        expmsg = "attributelevelrights:"
        check1 = role_show(multihost.master, self.role_name,
                           ['--all',
                            '--rights'])
        if expmsg not in check1.stdout_text:
            pytest.fail("Verifying Role show with rights failed")

    def test_0002_raw(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to role show with option raw
        """
        role_show(multihost.master, self.role_name,
                  ['--raw'])
