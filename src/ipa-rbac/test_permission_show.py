"""
Test suite to verify permission-show option
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.permission_utils import permission_show, permission_add, permission_del


class TestPermissionShowPositive(object):
    """
    Positive testcases related to permission-show
    """

    def test_0001_show_rights(self, multihost):
        """
        IDM-IPA-TC : rbac : Function to show permission with rights
        """
        permission_name = "ManageUser"

        rights = ['objectclass', 'aci', 'cn', 'member', 'businesscategory', 'seealso', 'owner',
                  'ou', 'o', 'description', 'ipapermissiontype', 'ipapermbindruletype',
                  'ipapermlocation', 'ipapermdefaultattr', 'ipapermincludedattr',
                  'ipapermexcludedattr', 'ipapermright', 'ipapermtargetfilter', 'ipapermtarget',
                  'ipapermtargetto', 'ipapermtargetfrom', 'nsaccountlock', 'targetgroup',
                  'memberof', 'type', 'attrs']

        multihost.master.kinit_as_admin()
        permission_add(multihost.master, permission_name, ['--setattr=owner=cn=test',
                                                           '--addattr=owner=cn=test2',
                                                           '--right=read',
                                                           '--right=write',
                                                           '--attr=carlicense',
                                                           '--attr=description',
                                                           '--type=user'])
        print("Permission {} added successfully".format(permission_name))
        check1a = permission_show(multihost.master, permission_name, ['--all', '--rights'])
        for attr in rights:
            value = "'{}': 'rscwo'".format(attr)
            assert value in check1a.stdout_text

        permission_del(multihost.master, permission_name)
