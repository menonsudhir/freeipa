"""
Certprofile Delete testsuite
"""
import re
import pytest
from datetime import datetime
from lib import certprofile_run, create_cert_cfg, caacl_run
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.qe_class import qe_use_class_setup


class TestCertProfileDelete(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        master1 = multihost.master
        multihost.realm = master1.domain.realm
        now = datetime.now().strftime("%y%m%d_%H%M%S")
        multihost.tempdir = "/tmp/test_%s/" % now
        master1.run_command(['mkdir', multihost.tempdir], raiseonerr=False)
        multihost.cacertfile = multihost.tempdir + 'caIPAservice.cfg'
        multihost.password = "Secret123"
        multihost.testuser = "testuser1"

        print("Using following hosts for Cert Profile Delete testcases")
        print("*" * 80)
        print("MASTER: %s" % master1.hostname)
        print("*" * 80)

        # Export caIPAservice Cert
        master1.kinit_as_admin()
        data = {'host': master1,
                'caIPAserviceCert': '',
                'out': multihost.cacertfile}
        certprofile_run(data)

    def test_0013_negative_cert_profile_delete_default(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Successfully delete default IPA profile

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        data = {'host': multihost.master,
                'caIPAserviceCert': '',
                'exp_code': '1',
                'op': 'del'}
        certprofile_run(data)

    def test_0014_negative_cert_profile_delete_nonexistent(self, multihost):
        """

        :Title: IDM-IPA-TC:  Certificate Profiles: Fail to delete non-existent profile

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated
        """

        # Kinit as admin
        multihost.master.kinit_as_admin()
        data = {'host': multihost.master,
                'testprofile_nonexistent': '',
                'exp_code': '2',
                'op': 'del'}
        certprofile_run(data)

    def class_teardown(self, multihost):
        """ Class teardown for cert profile delete """
        multihost.master.run_command(['rm', '-rf', multihost.tempdir],
                                     raiseonerr=False)
