"""
CA ACLs host/hostgroup testsuite
"""
import re
import pytest
from datetime import datetime
from lib import certprofile_run, create_cert_cfg, caacl_run
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.qe_class import qe_use_class_setup


class TestCaAclHost(object):
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

        print("\nUsing following hosts for CA ACLs Host / "
              "Hostgroup testcases")
        print("*" * 80)
        print("MASTER: %s" % master1.hostname)
        print("*" * 80)

        # Export caIPAservice Cert
        master1.kinit_as_admin()
        data = {'host': master1,
                'caIPAserviceCert': '',
                'out': multihost.cacertfile}
        certprofile_run(data)

    def test_0036_positive_caacls_host_create(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully add host to CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated
        """
        cname = "testacl_0008"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        # Create acl
        caacl_run(data)

        # Add host to newly create acl
        data['hosts'] = multihost.master.hostname
        data['op'] = 'add-host'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             remove host from CA ACL
        # Remove host from CA ACL
        data['op'] = 'remove-host'
        caacl_run(data)

        # Delete acl
        data['op'] = 'del'
        caacl_run(data)

    def test_0037_positive_caacls_host_add_multiple_hosts(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully add multiple hosts to CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        cname = "testacl_0009"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        # Create acl
        caacl_run(data)

        hosts = ['server-0037-1', 'server-0037-2']
        for i in hosts:
            multihost.master.qerun(['ipa', 'host-add',
                                    i + "." + multihost.master.domain.name,
                                    '--force'],
                                   exp_returncode=0)

        # Add host to newly create acl
        data['hosts'] = hosts
        data['op'] = 'add-host'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully remove
        #             multiple hosts from CA ACL
        # Remove hosts from CA ACL
        data['op'] = 'remove-host'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs:
        #               Fail to remove non-existent host from CA ACL
        data['exp_code'] = '1'
        data['op'] = 'remove-host'
        caacl_run(data)

        # Delete hosts
        for i in hosts:
            multihost.master.qerun(['ipa', 'host-del',
                                    i + "." + multihost.master.domain.name],
                                   exp_returncode=0)
        # Delete acl
        del data['hosts']
        data['exp_code'] = '0'
        data['op'] = 'del'
        caacl_run(data)

    def test_0038_positive_caacls_hostgroup_create(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully add hostgroup to CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        cname = "testacl_0010"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        # Create acl
        caacl_run(data)

        # Add hostgroup
        hostgroup = "testacl_hg_0010"
        multihost.master.qerun(['ipa', 'hostgroup-add', hostgroup],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'hostgroup-add-member',
                                hostgroup,
                                '--hosts=' + multihost.master.hostname],
                               exp_returncode=0)

        # Add host to newly create acl
        data['hostgroups'] = hostgroup
        data['op'] = 'add-host'
        caacl_run(data)

        # Remove host from CA ACL
        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             remove hostgroup from CA ACL
        data['op'] = 'remove-host'
        caacl_run(data)

        # Delete acl
        data['op'] = 'del'
        caacl_run(data)
        # Delete hostgroup
        multihost.master.qerun(['ipa', 'hostgroup-del', hostgroup],
                               exp_returncode=0)

    def test_0039_positive_caacls_hg_create_multiple_hosts(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully add multiple hostgroups to CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        cname = "testacl_0011"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        # Create acl
        caacl_run(data)

        # Add hostgroup
        hostgroups = ["testacl_hg_0011", "testacl_hg_0012"]
        for hostgroup in hostgroups:
            multihost.master.qerun(['ipa', 'hostgroup-add', hostgroup],
                                   exp_returncode=0)
            multihost.master.qerun(['ipa', 'hostgroup-add-member',
                                    hostgroup,
                                    '--hosts=' + multihost.master.hostname],
                                   exp_returncode=0)

        # Add host to newly create acl
        data['hostgroups'] = hostgroups
        data['op'] = 'add-host'
        caacl_run(data)

        # Remove hostgroups from CA ACLS
        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully remove
        #             multiple hostgroups from CA ACL
        data['op'] = 'remove-host'
        caacl_run(data)

        # Delete acl
        data['op'] = 'del'
        caacl_run(data)
        # Delete hostgroup
        for hostgroup in hostgroups:
            multihost.master.qerun(['ipa', 'hostgroup-del', hostgroup],
                                   exp_returncode=0)

    def test_0064_negative_caacls_host_create(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs:  Fail to add host to non-existent CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        cname = "testacl_0012"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '2',
                'exp_output': 'CA ACL not found',
                'hosts': multihost.master.hostname,
                'op': 'add-host'}
        # Add host to non-existent ca acl
        caacl_run(data)

    def test_0040_negative_caacls_non_existent_host_create(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to add non-existent host to CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        cname = "testacl_0013"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        # Create acl
        caacl_run(data)
        # Add host to newly create acl
        data['exp_code'] = '1'
        data['exp_output'] = 'no such entry'
        data['hosts'] = "dne." + multihost.master.hostname
        data['op'] = 'add-host'
        caacl_run(data)

        # Remove non-existent host from CA ACL
        data['exp_output'] = 'This entry is not a member'
        data['op'] = 'remove-host'
        caacl_run(data)

        data['exp_code'] = '0'
        del data['exp_output']
        data['op'] = 'del'
        caacl_run(data)

    def test_0041_negative_caacls_non_existent_hg_create(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to add non-existant hostgroup to CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        cname = "testacl_0014"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        caacl_run(data)

        data['exp_code'] = '1'
        data['exp_output'] = 'no such entry'
        data['hostgroups'] = 'dne.hostgroup1'
        data['op'] = 'add-host'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to remove
        #             non-existent group from CA ACL
        data['exp_output'] = 'This entry is not a member'
        data['op'] = 'remove-host'
        caacl_run(data)

        # Delete acl
        data['exp_code'] = '0'
        del data['exp_output']
        del data['hostgroups']
        data['op'] = 'del'
        caacl_run(data)

    def class_teardown(self, multihost):
        """ class teardown for CA ACLs host / hostgroup testsuite"""
        multihost.master.run_command(['rm', '-rf', multihost.tempdir],
                                     raiseonerr=False)
