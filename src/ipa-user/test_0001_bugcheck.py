"""
Overview:
SetUp Requirements:
IPA Server configured on RHEL7.1
IPA Client configured on RHEL7.2
"""

import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.user_utils import add_ipa_user, del_ipa_user, user_find


class Testipauserfind(object):

    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print "\nClass Setup"
        print "MASTER: ", multihost.master.hostname
        print "CLIENT: ", multihost.client.hostname

    def test_0001_ipauserfinderror(self, multihost):
        """
        IDM-IPA-TC: ipa user-find: ipa user-find gives
                    error when run on RHEL7.1 IPA client
        """
        realm = multihost.master.domain.realm
        multihost.client.kinit_as_admin()
        multihost.client.qerun(['ipa', 'user-find'], exp_returncode=1,
                               exp_output="ipa: ERROR:")

    def test_0002_ipauserskipversioncheck(self, multihost):
        """
        Test to verify Bugzilla 1211589 - [RFE] Add option to skip
        the verify_client_version
        IDM-IPA-TC: ipa user-find: ipa -e skip_version_check=1
                    user-find works without any error on RHEL7.1 client
        """
        realm = multihost.master.domain.realm
        multihost.client.kinit_as_admin()
        multihost.client.qerun(['ipa', '-e', 'skip_version_check=1',
                               'user-find'], exp_returncode=0,
                               exp_output="1 user matched")

    def test_0003_bz1288967(self, multihost):
        """
        Test to verify Bugzilla 1288967 - Normalize Manager entry in ipa
        user-add
        """
        multihost.master.kinit_as_admin()
        testuser1 = 'testuser_1288967'
        testuser2 = 'testmgr_1288967'
        opt = {'manager': testuser2}
        add_ipa_user(multihost.master, testuser2)
        add_ipa_user(multihost.master, testuser1, options=opt)
        # Manager info is shown in '--all' of user-find command
        opt['all'] = ''
        cmd = user_find(multihost.master, options=opt)
        if cmd.returncode == 0:
            if 'Manager: ' + testuser2 in cmd.stdout_text:
                del_ipa_user(multihost.master, testuser1)
                del_ipa_user(multihost.master, testuser2)
                print("BZ1288967 verified")
            else:
                del_ipa_user(multihost.master, testuser1)
                del_ipa_user(multihost.master, testuser2)
                pytest.fail("BZ1288967 failed to verify")
        else:
            del_ipa_user(multihost.master, testuser1)
            del_ipa_user(multihost.master, testuser2)
            pytest.fail("Failed to run user-find command")
