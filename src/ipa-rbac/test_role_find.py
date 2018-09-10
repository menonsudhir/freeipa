"""
Overview:
Test suite to verify rbac role-find option
"""

from __future__ import print_function
import pytest
from ipa_pytests.shared.role_utils import role_find
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import


class TestRoleFind(object):
    """
    Testcases related to role-find
    """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_name(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to role find with option name
        """
        criteria1 = "--name=helpdesk"
        expmsg = "Number of entries returned 1"
        check1 = role_find(multihost.master, None,
                           [criteria1])
        if expmsg not in check1.stdout_text:
            pytest.fail("Couldn't find role using option name")

    def test_0002_desc_raw(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to role find with options desc and raw
        """
        criteria2 = "--desc=Helpdesk"
        expmsg1 = "Number of entries returned 1"
        check2 = role_find(multihost.master, None,
                           [criteria2])
        if expmsg1 not in check2.stdout_text:
            pytest.fail("Could't find role with options desc and raw")

    def test_0003_missing_name(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to role find with option missing name
        """
        check3 = role_find(multihost.master, None,
                           ['--name'], False)
        expmsg = "ipa: error: --name option requires 1 argument"
        if expmsg not in check3.stderr_text:
            print(check3.stderr_text)
            pytest.fail("This test should have failed")

    def test_0004_blank_desc(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to role find with option blank description
        """
        role_find(multihost.master, None,
                  ['--desc='])

    def test_0005_sizelimit(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to role find with option sizelimit
        """
        criteria5 = "--sizelimit=2"
        expmsg = "Number of entries returned 2"
        check5 = role_find(multihost.master, None,
                           [criteria5])
        if expmsg not in check5.stdout_text:
            pytest.fail("error in finding roless with specified sizelimit")

    def test_0006_pkey(self, multihost):
        """
        IDM-IPA-TC : rbac : pkey only test of ipa role
        """
        criteria6 = '--pkey-only'
        role_find(multihost.master, None,
                  [criteria6])
