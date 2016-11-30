"""
Overview:
TestSuite to verify BZs related to rbac
SetUp Requirements:
-Latest version of RHEL OS
-Need to test for Master
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.permission_utils import permission_add, permission_del
from ipa_pytests.shared.permission_utils import permission_show, permission_mod


class TestBugCheck(object):
    """ Test Class """

    @pytest.mark.tier1
    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0018_bz893850(self, multihost):
        """
        Test to verify bz893850 - modify permission with option permissions
        :param multihost:
        :return:
        """
        permission_name = "Permission_bz893850"
        multihost.master.kinit_as_admin()
        permission_add(multihost.master, permission_name,
                       ['--right=write',
                        '--type=user',
                        '--attr=description'])
        check18 = permission_mod(multihost.master, permission_name,
                                 ['--right=add',
                                  '--right=write'])
        exp_output18a = 'Modified permission "'+permission_name+'"'
        exp_output18b = 'Granted rights: write, add'
        if exp_output18a in check18.stdout_text and exp_output18b in check18.stdout_text:
            print("bz893850 verified successfully")
        else:
            pytest.xfail("Verification of bz893850 failed")
        permission_del(multihost.master, permission_name)

    def test_0019_bz817909(self, multihost):
        """
        Function to verify bz817909 - modify permission invalid attrs should show exact
        reason for failure
        :param multihost:
        :return:
        """
        permission_name = "Permission_bz817909"
        multihost.master.kinit_as_admin()
        permission_add(multihost.master, permission_name,
                       ['--right=write',
                        '--type=user',
                        '--attr=description'])
        attrs = "xyz"
        check19 = permission_mod(multihost.master, permission_name,
                                 ['--attrs='+attrs],
                                 False)
        exp_putput = 'ipa: ERROR: targetattr "'+attrs+'" does not exist in schema.'
        if exp_putput in check19.stderr_text:
            print("bz817909 verified successfully")
        else:
            pytest.xfail("verification of bz817909 failed")
        permission_del(multihost.master, permission_name)

    def test_0020_bz837357(self, multihost):
        """
        Function to verify bz837357 - Attributelevelrights should be same in
        permission-show and permission-mod for the same permission
        :param multihost:
        :return:
        """
        permission_name = "Permission_bz837357"
        multihost.master.kinit_as_admin()
        permission_add(multihost.master, permission_name,
                       ['--right=write',
                        '--type=user',
                        '--attr=cn'])
        check20 = permission_mod(multihost.master, permission_name,
                                 ['--attrs=cn',
                                  '--attrs=uid',
                                  '--all',
                                  '--rights'])
        exp_putput = permission_show(multihost.master, permission_name,
                                     ['--all',
                                      '--rights'])
        if exp_putput.stdout_text in check20.stdout_text:
            print("bz837357 verified successfully")
        else:
            pytest.xfail("verification of bz837357 failed")
        permission_del(multihost.master, permission_name)
