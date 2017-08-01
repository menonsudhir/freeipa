"""
Certprofile Find testsuite
"""
import re
import pytest
from datetime import datetime
from lib import certprofile_run, create_cert_cfg, caacl_run
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.qe_class import qe_use_class_setup


class TestCertProfileFind(object):
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

        print("\nUsing following hosts for Cert Profile Find testcases")
        print("*" * 80)
        print("MASTER: %s" % master1.hostname)
        print("*" * 80)

        # Export caIPAservice Cert
        master1.kinit_as_admin()
        data = {'host': master1,
                'caIPAserviceCert': '',
                'out': multihost.cacertfile}
        certprofile_run(data)

    def test_0015_positive_cert_profile_find(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Successfully find all profiles

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated
        """

        # Kinit as admin
        multihost.master.kinit_as_admin()
        data = {'host': multihost.master,
                'exp_code': '0',
                'exp_output': 'Number of entries returned',
                'op': 'find'}
        certprofile_run(data)

    def test_0016_positive_cert_profile_find_custom(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Successfully find custom profile config

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        # Create a sample configuration
        cname = 'testprofile_find'
        cname_file = '{}{}.cfg'.format(multihost.tempdir, cname)
        cert_data = {'host': multihost.master,
                     'name': cname,
                     'desc': cname + '_cert',
                     'cacert': multihost.cacertfile,
                     'opfile': cname_file}
        create_cert_cfg(cert_data)

        # Import a newly create configuration file
        data = {'host': multihost.master,
                'store': 'True',
                cname: '',
                'desc': cert_data['desc'],
                'file': cert_data['opfile'],
                'exp_code': '0',
                'op': 'import'}
        certprofile_run(data)
        # Remove unwanted elements from data dict.
        for key in ['store', 'desc', 'file', cname]:
            data.pop(key)
        data['id'] = cname
        data['exp_output'] = 'Number of entries returned 1'
        data['op'] = 'find'
        # Test case to find by id
        certprofile_run(data)

        # Test case to find by description
        data.pop('id')
        data['desc'] = cert_data['desc']
        data['exp_output'] = 'Number of entries returned 1'
        data['op'] = 'find'
        certprofile_run(data)

        # Test case to find by invalid description
        data['desc'] = 'invalide'
        data['exp_code'] = '1'
        data['exp_output'] = 'Number of entries returned 0'
        certprofile_run(data)

        # Test case to find by profile name
        data.pop('desc')
        data[cname] = ''
        data['exp_code'] = '0'
        data['exp_output'] = 'Number of entries returned 1'
        certprofile_run(data)

        # Cleanup
        data['exp_output'] = ''
        data['op'] = 'del'
        certprofile_run(data)

    def test_0017_negative_cert_profile_find_invalid(self, multihost):
        """

        :Title: IDM-IPA-TC:  Certificate Profiles: Fail to find profile by invalid id

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated
        """

        # Kinit as admin
        multihost.master.kinit_as_admin()
        cname = 'testprofile_invalid_find'
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '1',
                'op': 'find'}
        # Test case: Fail to find profile by non-existent description
        certprofile_run(data)

        # Test case:  Fail to find profile by invalid id
        del data[cname]
        data['%123' + cname] = ''
        certprofile_run(data)

        # Test case:  Fail to find profile by id
        del data['%123' + cname]
        data['id'] = cname
        certprofile_run(data)

        # Test case:  Successfully find profiles with store True
        del data['id']
        data['store'] = 'True'
        data['exp_code'] = '0'
        certprofile_run(data)

        # Test case: Successfully find profiles with store False
        data['store'] = 'False'
        data['exp_code'] = '0'
        data['exp_output'] = 'Number of entries returned 1'
        certprofile_run(data)

        # Test case: Fail to find profiles with invalid store value
        data['store'] = 'invalid_value'
        data['exp_code'] = '1'
        data['exp_output'] = 'must be True or False'
        certprofile_run(data)

    def class_teardown(self, multihost):
        """ Class teardown for cert profile find """
        print("Running class teardown for cert profile find")
        multihost.master.run_command(['rm', '-rf', multihost.tempdir],
                                     raiseonerr=False)
