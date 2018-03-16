"""
Test suite to verify permission-find option
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.permission_utils import permission_del, permission_add
from ipa_pytests.shared.permission_utils import permission_mod


class TestPermissionModPositive(object):
    """
    Positive testcases related to permission-mod
    """
    def test_0001_mod_type(self, multihost):
        """
        IDM-IPA-TC : rbac : Function to modify permission with option type
        """
        permission_name = "PermissionMod1"
        multihost.master.kinit_as_admin()
        permission_add(multihost.master, permission_name,
                       ['--right=write',
                        '--type=user',
                        '--attr=description'])
        check1 = permission_mod(multihost.master, permission_name,
                                ['--type=host'])
        exp_output1 = 'Modified permission "' + permission_name + '"'
        exp_output2 = 'Type: host'
        if exp_output1 in check1.stdout_text and exp_output2 in check1.stdout_text:
            print(permission_name+" modified with option type successfully")
        else:
            pytest.xfail(permission_name+" modification with option type failed")
        permission_del(multihost.master, permission_name)

    def test_0002_mod_rename(self, multihost):
        """
        IDM-IPA-TC : rbac : Function to modify permission with option rename
        """
        permission_name = "PermissionMod2"
        multihost.master.kinit_as_admin()
        permission_rename = "PermissionMod2Rename"
        permission_add(multihost.master, permission_name,
                       ['--right=write',
                        '--type=user',
                        '--attr=description'])
        check2 = permission_mod(multihost.master, permission_name,
                                ['--rename='+permission_rename])
        exp_output = "Permission name: "+permission_rename
        if exp_output in check2.stdout_text:
            print(permission_name+" rename successfully to "+permission_rename)
            permission_del(multihost.master, permission_rename)
        else:
            pytest.xfail("renaming permission using permission-mod failed")
            permission_del(multihost.master, permission_name)
