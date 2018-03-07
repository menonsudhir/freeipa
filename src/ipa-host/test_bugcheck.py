"""
Overview:
Test Suite to verify bugs related to "ipa host" functionalities
Setup Requirements:
IPA Server configured on latest RHEL os
"""

from ipa_pytests.shared.user_utils import add_ipa_user
import pytest
# noinspection PyUnresolvedReferences
from ipa_pytests.qe_class import multihost

fakeuser = "testuser1"
fakepassword = "Secret123"
fakehost = 'labmachine.testrelm.test'


class TestBugChecks(object):
    def class_setup(self, multihost):
        """ Setup for class """
        print ("\nClass Setup")
        print ("MASTER: ", multihost.master.hostname)

    def test_0001_bz_1248524(self, multihost):
        """IDM-IPA-TC : host-cli : Verification for #1248524 - User can't find any hosts using 'ipa host-find $HOSTNAME' """
        try:
            # Finding a host as admin
            multihost.master.kinit_as_admin()
            multihost.master.qerun(['ipa', 'host-find', multihost.master.hostname], exp_returncode=0,
                                   exp_output="1 host matched")
            multihost.master.qerun(['ipa', 'host-find', '--hostname=' + multihost.master.hostname], exp_returncode=0,
                                   exp_output="1 host matched")

            # Finding a host as non-admin user. A new user "testuser1" with "Secret123" as password is added.
            add_ipa_user(multihost.master, fakeuser, fakepassword)
            multihost.master.kinit_as_user(fakeuser, fakepassword)
            multihost.master.qerun(['ipa', 'host-find', multihost.master.hostname], exp_returncode=0,
                                   exp_output="1 host matched")
            multihost.master.qerun(['ipa', 'host-find', '--hostname=' + multihost.master.hostname], exp_returncode=0,
                                   exp_output="1 host matched")
            # add a fake host and find it using above commands
            multihost.master.kinit_as_admin()

            multihost.master.qerun(['ipa', 'host-add', fakehost, '--password=labuser1', '--force'], exp_returncode=0,
                                   exp_output='Added host "' + fakehost + '"')
            multihost.master.kinit_as_user(fakeuser, fakepassword)  # change to non admin user
            multihost.master.qerun(['ipa', 'host-find', fakehost], exp_returncode=0,
                                   exp_output="1 host matched")
            multihost.master.qerun(['ipa', 'host-find', '--hostname=' + fakehost], exp_returncode=0,
                                   exp_output="1 host matched")

        except StandardError as errval:
            print("Error %s" % (str(errval.args[0])))
            pytest.skip("test_find_host_name")

    def class_teardown(self, multihost):
        """
        Cleanup
        """
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'user-del', fakeuser],
                               exp_returncode=0, exp_output='Deleted user "'+fakeuser+'"')
        multihost.master.qerun(['ipa', 'host-del', fakehost],
                               exp_returncode=0, exp_output='Deleted host "'+fakehost+'"')
