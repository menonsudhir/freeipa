"""
Overview:
Test suite to verify rbac privilege-find option
"""

from __future__ import print_function
import pytest
from ipa_pytests.shared.privilege_utils import privilege_find
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import


class TestPrivilegeFind(object):
    """
    Testcases related to privilege-find
    """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_name(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to privilege find with option name
        """
        criteria1 = "--name=Automount Administrators"
        expmsg1 = "Privilege name: Automount Administrators"
        expmsg2 = "Number of entries returned 1"
        check1 = privilege_find(multihost.master, None,
                                options_list=[criteria1])
        if expmsg1 not in check1.stdout_text or expmsg2 not in check1.stdout_text:
            pytest.fail("Couldn't find privilege using option name")

    def test_0002_desc_raw(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to privilege find with options desc and raw
        """
        criteria2 = "--desc=Automount Administrators"
        expmsg1 = "Description: Automount Administrators"
        expmsg2 = "Number of entries returned 1"
        check2 = privilege_find(multihost.master, None,
                                options_list=[criteria2])
        if expmsg1 not in check2.stdout_text or expmsg2 not in check2.stdout_text:
            pytest.fail("Could't find privilege with options desc and raw")

    def test_0003_missing_name(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to privilege find with option missing name
        """
        privilege_find(multihost.master, None,
                       ['--name='])

    def test_0004_blank_desc(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to privilege find with option blank description
        """
        privilege_find(multihost.master, None,
                       ['--desc='])

    def test_0005_sizelimit(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to privilege find with option sizelimit
        """
        criteria5 = "--sizelimit=2"
        expmsg = "Number of entries returned 2"
        check5 = privilege_find(multihost.master, None,
                                options_list=[criteria5])
        if expmsg not in check5.stdout_text:
            pytest.fail("error in finding privilieges with specified sizelimit")

    def test_0006_pkey(self, multihost):
        """
        IDM-IPA-TC : rbac : pkey only test of ipa privilege
        """
        criteria6 = '--pkey-only'
        privilege_find(multihost.master, None,
                       options_list=[criteria6])
