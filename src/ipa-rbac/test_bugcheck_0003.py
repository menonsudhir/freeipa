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
from ipa_pytests.shared.privilege_utils import privilege_add, privilege_del
from ipa_pytests.shared.privilege_utils import privilege_find, privilege_remove_permission
from ipa_pytests.shared.privilege_utils import privilege_add_permission, privilege_show


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
        IDM-IPA-TC : rbac : Test to verify bz893850 - modify permission with option permissions
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
        IDM-IPA-TC : rbac : Function to verify bz817909 - modify permission invalid attrs should show exact reason for failure
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
        IDM-IPA-TC : rbac : Function to verify bz837357 - Attributelevelrights should be same in permission-show and permission-mod for the same permission
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

    def test_0021_bz742327_bz893186_bz997085(self, multihost):
        """
        IDM-IPA-TC : rbac : Function to verify bz742327, bz893186, bz997085: Check IPA provided Privileges have assigned Permissions
        """
        multihost.master.kinit_as_admin()
        check21a = privilege_find(multihost.master)
        if check21a is not None:
            check21a = check21a.stdout_text.split("\n")
        for line in check21a:
            if "Privilege name" in line:
                privilege_name = line.split(":")[1].strip()
                check21c = privilege_show(multihost.master, privilege_name, ['--all'])
                if "Permissions:" not in check21c.stdout_text:
                    pytest.fail(privilege_name + " doesn't have any permission")

    def test_0022_bz816574(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify bz816574 - add privilege with blank setattr should work
        """
        privilege_name = "Add User with blank attr"
        privilege_desc = "--desc=Add User with blank attr"
        attr = "--setattr="
        privilege_add(multihost.master, privilege_name,
                      [privilege_desc,
                       attr])
        privilege_del(multihost.master, privilege_name)

    def test_0023_bz955699(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify bz955699 - Host administrator privilege should have certificate access
        """
        privilege_name = "Host Administrators"
        check23 = privilege_show(multihost.master, privilege_name)
        check23a = "Revoke Certificate"
        check23b = "Retrieve Certificates from the CA"
        if check23a not in check23.stdout_text or check23b not in check23.stdout_text:
            print(check23.stdout_text)
            pytest.fail("Verification of bz955699 failed")

    def test_0024_bz816624(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify bz816624 - add blank permission to privilege shouldn't throw internal error
        """
        privilege_name = "Add User"
        expmsg = "Number of permissions added 0"
        privilege_add(multihost.master, privilege_name)
        check24 = privilege_add_permission(multihost.master, privilege_name,
                                           ['--permission='],
                                           False)
        if expmsg not in check24.stdout_text:
            print(check24.stderr_text)
            pytest.fail("Verification of bz816624 failed")
        privilege_del(multihost.master, privilege_name)

    def test_0025_bz797916(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify bz797916 - Should be able to remove the permission from the privilege
        """
        privilege_name = "HBAC Administrator"
        permission_name = "System: Add HBAC Rule"
        check25 = privilege_remove_permission(multihost.master, privilege_name,
                                              ['--permission='+permission_name])
        if permission_name in check25.stdout_text:
            pytest.fail("Verification of bz797916 failed")
        privilege_add_permission(multihost.master, privilege_name,
                                 ['--permission='+permission_name])

    def test_0026_bz816624(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to verify bz816624 - remove blank permission from privilege should not throw internal error
        """
        privilege_name = "HBAC Administrator"
        expmsg = "Number of permissions removed 0"
        check26 = privilege_remove_permission(multihost.master, privilege_name,
                                              ["--permission="])
        if expmsg not in check26.stdout_text:
            pytest.fail("Verification of bz816624 failed")
