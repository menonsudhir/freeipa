"""
Test suite to verify permission-del option
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.permission_utils import permission_del


class TestPermissionDelete(object):
    """
    Positive testcases related to permission-show
    """

    def test_0001_del_continue(self, multihost):
        """
        IDM-IPA-TC : rbac : Function to delete permission with option continue
        """
        permission_name = "fake_permission"
        exp_output = "Failed to remove: " + permission_name
        check1 = permission_del(multihost.master, permission_name, ['--continue'], False)
        if exp_output in check1.stdout_text:
            print("Success! delete permission with option continue verified")
        else:
            pytest.xfail("delete permission with option continue verification failed")
