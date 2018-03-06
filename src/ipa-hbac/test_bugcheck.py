"""
Overview:
Test suite to verify hbac options
"""

import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.shared.utils import kinit_as_user
from ipa_pytests.shared.hbac_utils import hbacrule_add
from ipa_pytests.shared.hbac_utils import hbacrule_del
from ipa_pytests.shared.hbac_utils import hbacrule_find

fakeuser = "testuser1"
fakepassword = "Secret123"
fakerule = "testrule1"


class TestBugCheck(object):
    """ Test Class """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_bz1243261(self, multihost):
        """
        IDM-IPA-TC: hbac : Test to check Bug 1243261 - non-admin users cannot search hbac rules
        """

        add_ipa_user(multihost.master, fakeuser, fakepassword)
        hbacrule_add(multihost.master, fakerule)
        multihost.master.kinit_as_admin()
        admin_op_all = hbacrule_find(multihost.master)
        admin_op_single = hbacrule_find(multihost.master, rulename=fakerule)
        kinit_as_user(multihost.master, fakeuser, fakepassword)
        hbacrule_find(multihost.master, exp_output=admin_op_all.stdout_text)
        hbacrule_find(multihost.master, rulename=fakerule, exp_output=admin_op_single.stdout_text)

    def class_teardown(self, multihost):
        """ Full suite teardown """
        multihost.master.kinit_as_admin()
        hbacrule_del(multihost.master, fakerule)
        multihost.master.qerun(['ipa', 'user-del', fakeuser])
