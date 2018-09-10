"""
Overview:
Test suite to verify rbac privilege-show option
"""

from __future__ import print_function
import pytest
from ipa_pytests.shared.privilege_utils import privilege_show
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import


class TestPrivilegeShow(object):
    """
    Testcases related to privilege-show
    """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_rights(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to show privilege with option rights
        """
        privilege_name = "Host Group Administrators"

        expmsg = "attributelevelrights: {'objectclass': 'rscwo', 'aci': 'rscwo', 'cn': 'rscwo', 'member': " \
                  "'rscwo', 'businesscategory': 'rscwo', 'seealso': 'rscwo', 'owner': 'rscwo', 'ou': 'rscwo', " \
                  "'o': 'rscwo', 'description': 'rscwo', 'memberof': 'rsc', 'nsaccountlock': 'rscwo'}"

        check1 = privilege_show(multihost.master, privilege_name,
                                options_list=['--all',
                                              '--rights'])
        if expmsg not in check1.stdout_text:
            pytest.fail("Verify Privilege show with rights failed")
