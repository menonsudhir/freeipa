"""
Certprofile Modify testsuite
"""
import re
import pytest
from datetime import datetime
from lib import certprofile_run, create_cert_cfg, caacl_run
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.qe_class import qe_use_class_setup


class TestCertProfileModify(object):
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

        print("\nUsing following hosts for Cert Profile Modify testcases")
        print("*" * 80)
        print("MASTER: %s" % master1.hostname)
        print("*" * 80)

        # Export caIPAservice Cert
        master1.kinit_as_admin()
        data = {'host': master1,
                'caIPAserviceCert': '',
                'out': multihost.cacertfile}
        certprofile_run(data)

    def test_0018_positive_cert_profile_modify(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Successfully change profile description

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        # Create a sample configuration
        cname = 'testprofile_mod'
        cname_file = '{}{}.cfg'.format(multihost.tempdir, cname)
        cert_data = {'host': multihost.master,
                     'name': cname,
                     'desc': cname + '_cert',
                     'cacert': multihost.cacertfile,
                     'opfile': cname_file}
        create_cert_cfg(cert_data)
        # Import a newly create configuration file
        data = {'host': multihost.master,
                'store': 'False',
                cname: '',
                'desc': cert_data['desc'],
                'file': cert_data['opfile'],
                'exp_code': '0',
                'op': 'import'}
        certprofile_run(data)
        data['op'] = 'show'
        certprofile_run(data)

        data['desc'] = 'new_' + cert_data['desc']
        # Remove unwanted elements from data dict.
        for key in ['store', 'file']:
            data.pop(key)
        data['op'] = 'mod'
        certprofile_run(data)

        # Remove unwanted elements from data dict.
        for key in [cname]:
            data.pop(key)
        data['exp_output'] = 'Profile description: ' + data['desc']
        data['op'] = 'find'
        certprofile_run(data)

        # Test case:  Successfully change profile store setting
        data[cname] = ''
        data['store'] = 'True'
        del data['desc']
        data['op'] = 'mod'
        certprofile_run(data)

        data['exp_output'] = 'Store issued certificates: TRUE'
        data['op'] = 'find'
        certprofile_run(data)

        # Cleanup
        del data['exp_output']
        data['exp_code'] = '0'
        data['op'] = 'del'
        certprofile_run(data)

    def test_0019_positive_cert_profile_modify_cfg(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Successfully change profile config from file

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        # Create a sample configuration
        cname = 'testprofile_cfg_mod'
        cname_file = '{}{}.cfg'.format(multihost.tempdir, cname)
        new_cname_file = '{}{}_changed.cfg'.format(multihost.tempdir, cname)
        cert_data = {'host': multihost.master,
                     'name': cname,
                     'desc': cname + '_cert',
                     'cacert': multihost.cacertfile,
                     'opfile': cname_file}
        create_cert_cfg(cert_data)
        # Import a newly create configuration file
        data = {'host': multihost.master,
                'store': 'False',
                cname: '',
                'desc': cert_data['desc'],
                'file': cert_data['opfile'],
                'exp_code': '0',
                'op': 'import'}
        certprofile_run(data)
        cfg = multihost.master.get_file_contents(cname_file)
        cfg = re.sub('1.3.6.1.5.5.7.3.1,1.3.6.1.5.5.7.3.2',
                     '1.3.6.1.5.5.7.3.4', cfg)
        multihost.master.put_file_contents(new_cname_file, cfg)

        # Import new changed cert profile
        data['file'] = new_cname_file
        # Remove unwanted elements from data dict.
        for key in ['store', 'desc']:
            data.pop(key)
        data['op'] = 'mod'
        certprofile_run(data)

        # Test case:  Fail to change profile store setting to invalid boolean
        # Remove unwanted elements from data dict.
        for key in ['file']:
            data.pop(key)

        data['store'] = 'invalid'
        data['exp_code'] = '1'
        certprofile_run(data)

        # Test case:  Fail to change profile name with setattr
        del data['store']
        data['setattr'] = 'cn=bogus'
        data['exp_code'] = '1'
        certprofile_run(data)

        # Cleanup
        data['exp_code'] = '0'
        data['op'] = 'del'
        certprofile_run(data)

    def test_0020_negative_cert_profile_mod_nonexistent(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Fail to change profile description for non-existent profile

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        data = {'host': multihost.master,
                'testprofile_mod_nonexistent': '',
                'exp_code': '2',
                'op': 'mod'}
        certprofile_run(data)

    def class_teardown(self, multihost):
        """ Class teardown for cert profile modify"""
        multihost.master.run_command(['rm', '-rf', multihost.tempdir],
                                     raiseonerr=False)
