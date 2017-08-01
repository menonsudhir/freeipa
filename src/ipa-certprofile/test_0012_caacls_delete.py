"""
Certprofile CA ACLs Delete testsuite
"""
import re
import pytest
from datetime import datetime
from lib import certprofile_run, create_cert_cfg, caacl_run
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.qe_class import qe_use_class_setup


class TestCaAclDelete(object):
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

        print("\nUsing following hosts for Cert Profile CA ACLs "
              "delete testcases")
        print("*" * 80)
        print("MASTER: %s" % master1.hostname)
        print("*" * 80)

        # Export caIPAservice Cert
        master1.kinit_as_admin()
        data = {'host': master1,
                'caIPAserviceCert': '',
                'out': multihost.cacertfile}
        certprofile_run(data)

    def test_0055_negative_caacls_delete_nonexistent_acl(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully continue when cannot delete CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()

        cname = "testacl_0025"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                '--continue': '',
                'exp_output': 'Failed to remove',
                'op': 'del'}
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to delete
        #             non-existent CA ACL
        del data['--continue']
        data['exp_code'] = '2'
        data['exp_output'] = 'CA ACL not found'
        data['op'] = 'del'
        caacl_run(data)

    def class_teardown(self, multihost):
        """ Class teardown for caacls delete """
        multihost.master.run_command(['rm', '-rf', multihost.tempdir],
                                     raiseonerr=False)
