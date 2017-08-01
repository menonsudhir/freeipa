"""
CA ACLs Service testsuite
"""
import re
import pytest
from datetime import datetime
from lib import certprofile_run, create_cert_cfg, caacl_run
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.qe_class import qe_use_class_setup


class TestCaAclService(object):
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

        print("\nUsing following hosts for CA ACLs Service testcases")
        print("*" * 80)
        print("MASTER: %s" % master1.hostname)
        print("*" * 80)

        # Export caIPAservice Cert
        master1.kinit_as_admin()
        data = {'host': master1,
                'caIPAserviceCert': '',
                'out': multihost.cacertfile}
        certprofile_run(data)

    def test_0043_positive_caacls_service_add(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Successfully add service to CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        # Add service
        service = "testservice_0043" + '/' + multihost.master.hostname
        multihost.master.qerun(['ipa', 'service-add', service, '--force'],
                               exp_returncode=0)

        cname = "testacl_0017"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        caacl_run(data)
        # Add service to newly create ACL
        data['services'] = service
        data['op'] = 'add-service'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             remove service from CA ACL
        # Delete CA ACL
        data['op'] = 'remove-service'
        caacl_run(data)
        # Delete service
        multihost.master.qerun(['ipa', 'service-del', service],
                               exp_returncode=0)
        # Delete CA ACL
        data['op'] = 'del'
        caacl_run(data)

    def test_0044_caacls_service_add_multiple_services(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Successfully add multiple service to CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        # Add service
        services = ["testservice_0044_1" + '/' + multihost.master.hostname,
                    "testservice_0044_2" + '/' + multihost.master.hostname]

        for service in services:
            multihost.master.qerun(['ipa', 'service-add',
                                    service, '--force'],
                                   exp_returncode=0)

        cname = "testacl_0018"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        caacl_run(data)
        # Add service to newly create ACL
        data['services'] = services
        data['op'] = 'add-service'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             remove multiple services from CA ACL
        # Delete CA ACL
        data['op'] = 'remove-service'
        caacl_run(data)

        # Delete service
        for service in services:
            multihost.master.qerun(['ipa', 'service-del', service],
                                   exp_returncode=0)
        # Delete CA ACL
        data['op'] = 'del'
        caacl_run(data)

    def test_0045_caacls_service_add_service_nonexistent_acl(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to add service to non-existent CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        # Add service
        service = "testservice_0045" + '/' + multihost.master.hostname
        multihost.master.qerun(['ipa', 'service-add', service, '--force'],
                               exp_returncode=0)

        cname = "testacl_0019"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '2',
                'services': service,
                'op': 'add-service'}
        # Add service to non-existent
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to remove
        #             service from non-existent CA ACL
        data['op'] = 'remove-service'
        caacl_run(data)

        # Delete added service
        multihost.master.qerun(['ipa', 'service-del', service],
                               exp_returncode=0)

    def test_0046_caacls_service_add_nonexistent_service_acl(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to add non-existent profile to CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        service = "testservice_0046" + '/' + multihost.master.hostname

        cname = "testacl_0019"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}

        caacl_run(data)
        # Add service to newly create ACL
        data['services'] = service
        data['exp_code'] = '1'
        # Add service to non-existent
        data['op'] = 'add-service'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to remove
        #             non-existent service from CA ACL
        data['op'] = 'remove-service'
        caacl_run(data)

        # Delete ca acl
        data['exp_code'] = '0'
        data['op'] = 'del'
        caacl_run(data)

    def test_bz1366626_caacls_fail_to_add_nonexistent_service(self, multihost):
        """
        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to add non-existent service to acl

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        service = 'bz1366626/' + multihost.master.hostname + \
                  '@' + multihost.master.domain.realm

        cname = 'testacl_bz1366626'
        data = {'host': multihost.master,
                'op': 'add',
                cname: '',
                'exp_code': '0'}
        caacl_run(data)

        data['op'] = 'add-service'
        data['services'] = service
        data['exp_code'] = '1'
        data['exp_output'] = service + ': no such entry'
        caacl_run(data)

        data['op'] = 'del'
        data['exp_code'] = '0'
        data['exp_output'] = None
        caacl_run(data)

    def class_teardown(self, multihost):
        """ Class teardown for caacls service """
        multihost.master.run_command(['rm', '-rf', multihost.tempdir],
                                     raiseonerr=False)
