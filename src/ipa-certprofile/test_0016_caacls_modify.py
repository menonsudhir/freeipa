"""
CA ACLs Modify testsuite
"""
import re
import pytest
from datetime import datetime
from lib import certprofile_run, create_cert_cfg, caacl_run
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.qe_class import qe_use_class_setup


class TestCaAclModify(object):
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

        print("\nUsing following hosts for CA ACLs Modify testcases")
        print("*" * 80)
        print("MASTER: %s" % master1.hostname)
        print("*" * 80)

        # Export caIPAservice Cert
        master1.kinit_as_admin()
        data = {'host': master1,
                'caIPAserviceCert': '',
                'out': multihost.cacertfile}
        certprofile_run(data)

    def test_0059_positive_caacls_mod_acl(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully change description for CA ACL

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()

        # create a new CA ACL
        cname = 'testacl_0059'
        cname_desc = 'testacl_0059_description'

        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        caacl_run(data)

        # Modify description
        data['desc'] = cname_desc
        data['exp_output'] = 'Description: ' + cname_desc
        data['op'] = 'mod'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully change
        #             profilecat to all for CA ACL
        del data['desc']
        data['profilecat'] = 'all'
        data['exp_output'] = 'Profile category: all'
        data['op'] = 'mod'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             change usercat to all for CA ACL
        del data['profilecat']
        data['exp_output'] = 'User category: all'
        data['usercat'] = 'all'
        data['op'] = 'mod'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             change hostcat to all for CA ACL
        del data['usercat']
        data['hostcat'] = 'all'
        data['exp_output'] = 'Host category: all'
        data['op'] = 'mod'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully change
        #             servicecat to all for CA ACL
        del data['hostcat']
        data['servicecat'] = 'all'
        data['exp_output'] = 'Service category: all'
        data['op'] = 'mod'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to change
        #             description for non-existent CA
        del data[cname]
        del data['exp_output']
        cname_dne = "non-existent-ca-acl-0059"
        data[cname_dne] = ''
        data['exp_code'] = '2'
        data['exp_output'] = 'CA ACL not found'
        data['op'] = 'mod'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully change
        #             profilecat to non-existent CA ACL
        data['profilecat'] = 'all'
        data['exp_output'] = 'CA ACL not found'
        data['op'] = 'mod'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully change
        #             usercat to non-existent CA ACL
        del data['profilecat']
        data['exp_output'] = 'CA ACL not found'
        data['usercat'] = 'all'
        data['op'] = 'mod'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully change
        #             hostcat to non-existent CA ACL
        del data['usercat']
        data['hostcat'] = 'all'
        data['exp_output'] = 'CA ACL not found'
        data['op'] = 'mod'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully change
        #             servicecat to non-existent CA ACL
        del data['hostcat']
        data['servicecat'] = 'all'
        data['exp_output'] = 'CA ACL not found'
        data['op'] = 'mod'
        caacl_run(data)

        # Clean up
        data['exp_code'] = 0
        del data['exp_output']
        del data[cname_dne]
        data[cname] = ''
        data['op'] = 'del'
        caacl_run(data)

    def test_0060_negative_caacls_mod_acl(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to change description for non-existent CA

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()

        # create a new CA ACL
        aclname = 'testacl_0060'

        acl_data = {'host': multihost.master,
                    aclname: '',
                    'exp_code': '0',
                    'op': 'add'}
        caacl_run(acl_data)

        cname = 'server'
        opfile = '{}{}.cfg'.format(multihost.tempdir, cname)
        newopfile = '{}{}_2.cfg'.format(multihost.tempdir, cname)
        # Create a sample configuration
        cert_data = {'host': multihost.master,
                     'name': cname,
                     'desc': cname + '_cert',
                     'cacert': multihost.cacertfile,
                     'opfile': opfile}
        # Create Certificate configuration
        create_cert_cfg(cert_data)

        cfg = multihost.master.get_file_contents(opfile)
        cfg = re.sub('1.3.6.1.5.5.7.3.1,1.3.6.1.5.5.7.3.2',
                     '1.3.6.1.5.5.7.3.2', cfg)
        multihost.master.put_file_contents(newopfile, cfg)

        cert_data_import = {'host': multihost.master,
                            cname: '',
                            'store': 'True',
                            'desc': cname + '_cert',
                            'file': newopfile,
                            'exp_code': '0',
                            'op': 'import'}
        certprofile_run(cert_data_import)

        acl_data['certprofiles'] = cname
        acl_data['op'] = 'add-profile'
        caacl_run(acl_data)

        # Modify ACL with profilecat=all
        del acl_data['certprofiles']
        acl_data['profilecat'] = 'all'
        acl_data['exp_code'] = '1'
        acl_data['exp_output'] = 'profile category cannot be set to \'all\' '\
                                 'while there are allowed profiles'
        acl_data['op'] = 'mod'
        caacl_run(acl_data)

        # Clean up
        cert_data_import['op'] = 'del'
        certprofile_run(cert_data_import)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to change usercat
        #             to all when user exists for CA ACL

        # Add IPA user
        testuser = "testuser_0060"
        add_ipa_user(multihost.master, testuser, multihost.password)

        # Add user to CA profile
        del acl_data['profilecat']
        del acl_data['exp_output']
        acl_data['users'] = testuser
        acl_data['exp_code'] = '0'
        acl_data['op'] = 'add-user'
        # Add user to CA ACL
        caacl_run(acl_data)

        # Modify ACL with usercat=all
        del acl_data['users']
        acl_data['usercat'] = 'all'
        acl_data['exp_code'] = '1'
        acl_data['exp_output'] = 'user category cannot be set to \'all\' ' \
                                 'while there are allowed users'
        acl_data['op'] = 'mod'
        caacl_run(acl_data)

        # Clean up
        multihost.master.qerun(['ipa', 'user-del', testuser],
                               exp_returncode=0)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to change hostcat to
        #             all when host exists for CA ACL
        del acl_data['usercat']
        del acl_data['exp_output']
        acl_data['hosts'] = multihost.master.hostname
        acl_data['exp_code'] = '0'
        acl_data['op'] = 'add-host'

        # Add hosts to CA ACL
        caacl_run(acl_data)

        # Modify ACL with hostcat=all
        del acl_data['hosts']
        acl_data['exp_code'] = '1'
        acl_data['hostcat'] = 'all'
        acl_data['exp_output'] = 'host category cannot be set to \'all\' ' \
                                 'while there are allowed hosts'
        acl_data['op'] = 'mod'
        caacl_run(acl_data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to change servicecat
        #             to all when service exists for CA ACL
        # Add service
        service = "testservice_0060" + '/' + multihost.master.hostname
        multihost.master.qerun(['ipa', 'service-add', service, '--force'],
                               exp_returncode=0)

        # Add service to newly create ACL
        acl_data['services'] = service
        del acl_data['exp_output']
        acl_data['exp_output'] = '0'
        acl_data['op'] = 'add-service'
        caacl_run(acl_data)

        # Modify ACL with hostcat=all
        del acl_data['services']
        del acl_data['hostcat']
        acl_data['exp_code'] = '1'
        acl_data['servicecat'] = 'all'
        acl_data['exp_output'] = 'service category cannot be set to \'all\' ' \
                                 'while there are allowed services'
        acl_data['op'] = 'mod'
        caacl_run(acl_data)

        # Delete CA ACL
        del acl_data['servicecat']
        del acl_data['exp_output']
        acl_data['exp_code'] = '0'
        acl_data['services'] = service
        acl_data['op'] = 'remove-service'
        caacl_run(acl_data)

        # Delete service
        multihost.master.qerun(['ipa', 'service-del', service],
                               exp_returncode=0)
        # Delete CA ACL
        acl_data['op'] = 'del'
        caacl_run(acl_data)

    def class_teardown(self, multihost):
        """ Class Teardown for CA ACLs modify """
        multihost.master.run_command(['rm', '-rf', multihost.tempdir],
                                     raiseonerr=False)
