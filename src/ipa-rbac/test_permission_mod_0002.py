"""
Test suite to verify permission-find option
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.permission_utils import permission_del, permission_add
from ipa_pytests.shared.permission_utils import permission_mod


class TestPermissionModNegative(object):
    """
    Negative testcases related to permission-mod
    """
    def test_0001_mod_inv_right(self, multihost):
        """
        IDM-IPA-TC : rbac : Function to modify permission invalid with option right
        """
        permission_name = "PermModNeg1"
        multihost.master.kinit_as_admin()
        permission_add(multihost.master, permission_name,
                       ['--right=write',
                        '--type=user',
                        '--attr=description'])
        check1 = permission_mod(multihost.master, permission_name,
                                ['--right=xyz'],
                                False)
        if check1.returncode != 0:
            print("Success! permission-mod with invalid right failed")
        else:
            pytest.xfail("This test should have failed!")
        permission_del(multihost.master, permission_name)

    def test_0002_mod_inv_type(self, multihost):
        """
        IDM-IPA-TC : rbac : Function to modify permission invalid with option type
        """
        permission_name = "PermModNeg2"
        multihost.master.kinit_as_admin()
        permission_add(multihost.master, permission_name,
                       ['--right=write',
                        '--type=user',
                        '--attr=description'])
        check1 = permission_mod(multihost.master, permission_name,
                                ['--type=users'],
                                False)
        exp_output = "ipa: ERROR: invalid 'type'"
        if exp_output in check1.stderr_text:
            print("Success! permission-mod with invalid type failed")
        else:
            pytest.xfail("This test should have failed!")
        permission_del(multihost.master, permission_name)
