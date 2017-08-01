"""
CA ACLs Find testsuite
"""
import re
import pytest
from datetime import datetime
from lib import certprofile_run, create_cert_cfg, caacl_run
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.qe_class import qe_use_class_setup


class TestCaAclsFind(object):
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

        print("\nUsing following hosts for CA ACLs Find testcases")
        print("*" * 80)
        print("MASTER: %s" % master1.hostname)
        print("*" * 80)

        # Export caIPAservice Cert
        master1.kinit_as_admin()
        data = {'host': master1,
                'caIPAserviceCert': '',
                'out': multihost.cacertfile}
        certprofile_run(data)

    def test_0058_positive_caacls_find_acl(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully find all CA ACLs

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()

        # Find all CA ACL
        data = {'host': multihost.master,
                'exp_code': '0',
                'exp_output': 'Number of entries returned',
                'op': 'find'}
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             find single CA ACL
        cname = 'testacl_0058'
        cname_desc = 'testacl_0058_description'
        data[cname] = ''
        data['desc'] = cname_desc
        data['profilecat'] = 'all'
        data['usercat'] = 'all'
        data['hostcat'] = 'all'
        data['op'] = 'add'
        del data['exp_output']

        caacl_run(data)
        # Find newly create CA ACLs
        data['exp_output'] = 'ACL name: ' + cname
        data['op'] = 'find'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             find CA ACL by name
        del data[cname]
        data['name'] = cname
        # Find newly create CA ACLs
        data['exp_output'] = 'ACL name: ' + cname
        data['op'] = 'find'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             find CA ACL by description
        del data['name']
        data['desc'] = cname_desc
        # Find newly create CA ACLs
        data['exp_output'] = 'ACL name: ' + cname
        data['op'] = 'find'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             find CA ACL by profilecat all
        del data['desc']
        data['profilecat'] = 'all'
        # Find newly create CA ACLs
        data['exp_output'] = 'ACL name: ' + cname
        data['op'] = 'find'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             find CA ACL by usercat all
        del data['profilecat']
        data['usercat'] = 'all'
        # Find newly create CA ACLs
        data['exp_output'] = 'ACL name: ' + cname
        data['op'] = 'find'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             find CA ACL by hostcat all
        del data['usercat']
        data['hostcat'] = 'all'
        # Find newly create CA ACLs
        data['exp_output'] = 'ACL name: ' + cname
        data['op'] = 'find'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             find CA ACL by timelimit
        del data['hostcat']
        data['timelimit'] = '1'
        # Find newly create CA ACLs
        data['exp_output'] = 'Number of entries returned'
        data['op'] = 'find'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             find CA ACL by sizelimit
        del data['timelimit']
        data['sizelimit'] = '1'
        # Find newly create CA ACLs
        data['exp_output'] = 'Number of entries returned'
        data['op'] = 'find'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             find CA ACL with pkey-only
        del data['sizelimit']
        data['pkey-only'] = 'noarg'
        # Find newly create CA ACLs
        data['exp_output'] = 'Number of entries returned'
        data['op'] = 'find'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to find
        #             non-existent CA ACL
        del data['pkey-only']
        cname_dne = 'non-existent-ca-acl'
        data[cname_dne] = ''
        data['exp_code'] = '1'
        # Find newly create CA ACLs
        data['exp_output'] = 'Number of entries returned 0'
        data['op'] = 'find'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to find
        #             non-existent CA ACL
        del data[cname_dne]
        data['name'] = cname_dne
        data['exp_code'] = '1'
        # Find newly create CA ACLs
        data['exp_output'] = 'Number of entries returned 0'
        data['op'] = 'find'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to find
        #             non-existent CA ACL
        del data['name']
        cname_dne_desc = 'non-existent-ca-acl-desc'
        data['desc'] = cname_dne_desc
        data['exp_code'] = '1'
        # Find newly create CA ACLs
        data['exp_output'] = 'Number of entries returned 0'
        data['op'] = 'find'
        caacl_run(data)

        # Clean up
        data['exp_code'] = 0
        data[cname] = ''
        del data['exp_output']
        data['op'] = 'del'
        caacl_run(data)

    def class_teardown(self, multihost):
        """ Class teardown for caacls find """
        multihost.master.run_command(['rm', '-rf', multihost.tempdir],
                                     raiseonerr=False)
