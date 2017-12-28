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
        Function to show permission with rights
        :param multihost:
        :return:
        """
        permission_name = "ManageUser"
        exp_output = "attributelevelrights: {u'ipapermright': u'rscwo', u'cn': u'rscwo', " \
                     "u'ipapermtarget': u'rscwo', u'ipapermtargetto': u'rscwo', u'attrs': " \
                     "u'rscwo', u'ipapermlocation': u'rscwo', u'ipapermincludedattr': u'rscwo', " \
                     "u'nsaccountlock': u'rscwo', u'ipapermtargetfrom': u'rscwo', " \
                     "u'ipapermbindruletype': u'rscwo', u'owner': u'rscwo', " \
                     "u'member': u'rscwo', u'type': u'rscwo', u'ipapermtargetfilter': u'rscwo', " \
                     "u'description': u'rscwo', u'businesscategory': u'rscwo', u'memberof': " \
                     "u'rscwo', u'seealso': u'rscwo', u'ipapermissiontype': u'rscwo', " \
                     "u'objectclass': u'rscwo', u'aci': u'rscwo', u'o': u'rscwo', " \
                     "u'ipapermdefaultattr': u'rscwo', u'ou': u'rscwo', u'targetgroup': " \
                     "u'rscwo', u'ipapermexcludedattr': u'rscwo'}"
        multihost.master.kinit_as_admin()
        check1 = permission_add(multihost.master, permission_name, ['--setattr=owner=cn=test',
                                                                    '--addattr=owner=cn=test2',
                                                                    '--right=read',
                                                                    '--right=write',
                                                                    '--attr=carlicense',
                                                                    '--attr=description',
                                                                    '--type=user'])
        if check1.returncode == 0:
            print("Permission " + permission_name + " added successfully")
            check1a = permission_show(multihost.master, permission_name, ['--all',
                                                                          '--rights'])
            if exp_output in check1a.stdout_text:
                print("Success! permission-show works as expected")
            else:
                pytest.xfail("Error occured in this test")
            permission_del(multihost.master, permission_name)
        else:
            pytest.xfail("Failed to add permission")
