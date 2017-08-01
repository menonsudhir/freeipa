"""
Certprofile CA ACLs Create testsuite
"""
import re
import pytest
from datetime import datetime
from lib import certprofile_run, create_cert_cfg, caacl_run
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.qe_class import qe_use_class_setup


class TestCaAclCreate(object):
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
              "create testcases")
        print("*" * 80)
        print("MASTER: %s" % master1.hostname)
        print("*" * 80)

        # Export caIPAservice Cert
        master1.kinit_as_admin()
        data = {'host': master1,
                'caIPAserviceCert': '',
                'out': multihost.cacertfile}
        certprofile_run(data)

    def test_0028_positive_caacls_create(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: CA ACLs: Successfully add CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        # Create a sample configuration
        cname = 'testacl_0001'
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        caacl_run(data)
        # Delete acl
        data['op'] = 'del'
        caacl_run(data)

    def test_0029_positive_caacls_create_desc(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully add CA ACL with description

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        cname = "testacl_0002"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'desc': cname + '_description',
                'op': 'add'}
        caacl_run(data)
        # Delete acl
        data['op'] = 'del'
        caacl_run(data)

    def test_0030_positive_caacls_create_profilecat(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully add CA ACL with profilecat all

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        cname = "testacl_0003"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'profilecat': 'all',
                'op': 'add'}
        caacl_run(data)
        # Delete acl
        data['op'] = 'del'
        caacl_run(data)

    def test_0031_positive_caacls_create_usercat(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully add CA ACL with usercat all

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        cname = "testacl_0004"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'usercat': 'all',
                'op': 'add'}
        caacl_run(data)
        # Delete acl
        data['op'] = 'del'
        caacl_run(data)

    def test_0032_positive_caacls_create_hostcat(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully add CA ACL with hostcat all

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        cname = "testacl_0005"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'hostcat': 'all',
                'op': 'add'}
        caacl_run(data)
        # Delete acl
        data['op'] = 'del'
        caacl_run(data)

    def test_0033_positive_caacls_create_servicecat(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully add CA ACL with servicecat all

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        cname = "testacl_0006"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'servicecat': 'all',
                'op': 'add'}
        caacl_run(data)
        # Delete acl
        data['op'] = 'del'
        caacl_run(data)

    def test_0034_negative_caacls_create_same_name(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to add CA ACL with same name

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        cname = "testacl_0007"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'servicecat': 'all',
                'op': 'add'}
        caacl_run(data)
        # Add same caacl with same name
        data['exp_code'] = '1'
        caacl_run(data)

        # Delete acl
        data['exp_code'] = '0'
        data['op'] = 'del'
        caacl_run(data)

    def test_0035_negative_caacls_create_default_acl(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to add default CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated
        """
        cname = "hosts_services_caIPAserviceCert"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '1',
                'exp_output': 'already exists',
                'op': 'add'}
        caacl_run(data)

    def class_teardown(self, multihost):
        """ Class teardown for caacls create """
        multihost.master.run_command(['rm', '-rf', multihost.tempdir],
                                     raiseonerr=False)
