"""
Certprofile CA ACLs Disable testsuite
"""
import re
import pytest
from datetime import datetime
from lib import certprofile_run, create_cert_cfg, caacl_run
from ipa_pytests.shared.user_utils import add_ipa_user, del_ipa_user
from ipa_pytests.qe_class import qe_use_class_setup


class TestCaAclDisable(object):
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

        print("\nUsing following hosts for CA ACLs Disable testcases")
        print("*" * 80)
        print("MASTER: %s" % master1.hostname)
        print("*" * 80)

        # Export caIPAservice Cert
        master1.kinit_as_admin()
        data = {'host': master1,
                'caIPAserviceCert': '',
                'out': multihost.cacertfile}
        certprofile_run(data)

    def test_0056_positive_cacls_disable_acl(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully disable CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated
        """
        # Kinit as admin
        multihost.master.kinit_as_admin()

        cname = "testacl_0026"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        caacl_run(data)

        # Disable CA ACL
        data['op'] = 'disable'
        caacl_run(data)

        testuser = "testuser_0056"
        # IPA-IPA-TC: Certificate Profiles CA ACLs: Successfully add
        #             user to disabled CA ACL
        # Add IPA user
        add_ipa_user(multihost.master, testuser, multihost.password)

        # Add user to CA ACL
        data['users'] = testuser
        data['exp_code'] = '0'
        data['op'] = 'add-user'
        caacl_run(data)

        # Enable CA ACL
        data['op'] = 'enable'
        caacl_run(data)

        # Delete CA ACL
        del data['users']
        data['op'] = 'del'
        caacl_run(data)

        # Delete user
        del_ipa_user(multihost.master, testuser)

    def class_teardown(self, multihost):
        """ Class teardown for caacls create """
        multihost.master.run_command(['rm', '-rf', multihost.tempdir],
                                     raiseonerr=False)
