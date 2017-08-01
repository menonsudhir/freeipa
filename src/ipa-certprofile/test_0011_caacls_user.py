"""
CA ACLs User and Group testsuite
"""
import re
import pytest
from datetime import datetime
from lib import certprofile_run, create_cert_cfg, caacl_run
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.qe_class import qe_use_class_setup


class TestCaAclUserGroup(object):
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

        print("\nUsing following hosts for CA ACLs User and Group testcases")
        print("*" * 80)
        print("MASTER: %s" % master1.hostname)
        print("*" * 80)

        # Export caIPAservice Cert
        master1.kinit_as_admin()
        data = {'host': master1,
                'caIPAserviceCert': '',
                'out': multihost.cacertfile}
        certprofile_run(data)

    def test_0047_positive_caacls_add_user_acl(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully add user to CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        multihost.testuser = "testuser_0047"

        # Add IPA user
        add_ipa_user(multihost.master, multihost.testuser, multihost.password)

        cname = "testacl_0019"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        caacl_run(data)

        data['users'] = multihost.testuser
        data['exp_code'] = '0'
        data['op'] = 'add-user'
        # Add user to CA ACL
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             remove user from CA ACL
        data['op'] = 'remove-user'
        caacl_run(data)

        # Cleanup
        data['op'] = 'del'
        caacl_run(data)
        multihost.master.qerun(['ipa', 'user-del', multihost.testuser],
                               exp_returncode=0)

    def test_0048_positive_caacls_add_multiple_user_acl(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully add multiple user to CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()

        users = ['testuser_0048', 'testuser_0049']
        # Add IPA user
        for user in users:
            add_ipa_user(multihost.master, user, multihost.password)

        cname = "testacl_0020"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        caacl_run(data)

        data['users'] = users
        data['exp_code'] = '0'
        data['op'] = 'add-user'
        # Add user to CA ACL
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully remove
        #             multiple users from CA ACL
        data['op'] = 'remove-user'
        caacl_run(data)

        # Cleanup
        data['op'] = 'del'
        caacl_run(data)
        for user in users:
            multihost.master.qerun(['ipa', 'user-del', user],
                                   exp_returncode=0)

    def test_0049_positive_caacls_add_group_acl(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully add group to CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        testgrp = "testgroup_0049"

        # Add IPA group
        multihost.master.qerun(['ipa', 'group-add', testgrp])

        cname = "testacl_0020"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        caacl_run(data)

        data['groups'] = testgrp
        data['exp_code'] = '0'
        data['op'] = 'add-user'
        # Add group to CA ACL
        caacl_run(data)

        # Delete group from CA ACL
        data['op'] = 'remove-user'
        # Add group to CA ACL
        caacl_run(data)

        # Clean up
        data['op'] = 'del'
        caacl_run(data)
        multihost.master.qerun(['ipa', 'group-del', testgrp],
                               exp_returncode=0)

    def test_0050_positive_caacls_add_multiple_group_acl(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully add multiple groups to CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        testgrps = ["testgroup_0050", "testgroup_0051"]

        # Add IPA group
        for testgrp in testgrps:
            multihost.master.qerun(['ipa', 'group-add', testgrp])

        cname = "testacl_0021"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        caacl_run(data)

        data['groups'] = testgrps
        data['exp_code'] = '0'
        data['op'] = 'add-user'
        # Add group to CA ACL
        caacl_run(data)
        # Delete group from CA ACL
        data['op'] = 'remove-user'
        caacl_run(data)
        # Clean up
        data['op'] = 'del'
        caacl_run(data)

        for testgrp in testgrps:
            multihost.master.qerun(['ipa', 'group-del', testgrp],
                                   exp_returncode=0)

    def test_0051_negative_caacls_add_user_nonexistent_acl(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to add user to non-existent CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        multihost.testuser = "testuser_0051"

        # Add IPA user
        add_ipa_user(multihost.master, multihost.testuser, multihost.password)

        cname = "testacl_0022"
        data = {'host': multihost.master,
                cname: '',
                'users': multihost.testuser,
                'exp_code': '2',
                'op': 'add-user'}
        # Add user to non existent CA ACL
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to remove user
        #             from non-existent CA ACL
        data['op'] = 'remove-user'
        caacl_run(data)

        # Cleanup
        multihost.master.qerun(['ipa', 'user-del', multihost.testuser],
                               exp_returncode=0)

    def test_0052_negative_caacls_add_nonexistent_user_acl(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to add non-existent user to CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        multihost.testuser = "testuser_0052"

        cname = "testacl_0023"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        caacl_run(data)
        data['users'] = multihost.testuser
        data['exp_code'] = '1'
        data['op'] = 'add-user'
        # Add user to CA ACL
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to remove
        #             non-existent user from CA ACL
        data['op'] = 'remove-user'
        caacl_run(data)

        # Clean up
        data['exp_code'] = '0'
        data['op'] = 'del'
        caacl_run(data)

    def test_0053_negative_caacls_add_group_nonexistent_acl(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to add group to non-existent CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        testgrp = "testgrp_0053"

        # Add IPA group
        multihost.master.qerun(['ipa', 'group-add', testgrp])

        cname = "testacl_0024"
        data = {'host': multihost.master,
                cname: '',
                'groups': testgrp,
                'exp_code': '2',
                'op': 'add-user'}

        # Add user to non existent CA ACL
        caacl_run(data)
        # Cleanup
        multihost.master.qerun(['ipa', 'group-del', testgrp],
                               exp_returncode=0)

    def test_0054_negative_caacls_add_nonexistent_group_acl(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to add non-existent group to CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        testgrp = "testgrp_0054"

        cname = "testacl_0025"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        caacl_run(data)

        data['groups'] = testgrp
        data['exp_code'] = '1'
        # Add non-existent group to CA ACL
        data['op'] = 'add-user'
        caacl_run(data)
        # Clean up
        del data['groups']
        data['exp_code'] = '0'
        data['op'] = 'del'
        caacl_run(data)

    def class_teardown(self, multihost):
        """ Class teardown for caacls user """
        multihost.master.run_command(['rm', '-rf', multihost.tempdir],
                                     raiseonerr=False)
