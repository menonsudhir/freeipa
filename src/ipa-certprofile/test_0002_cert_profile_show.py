"""
Certprofile Show testsuite
"""
import re
import pytest
from datetime import datetime
from lib import certprofile_run, create_cert_cfg, caacl_run
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.qe_class import qe_use_class_setup


class TestCertProfileShow(object):
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

        print("Using following hosts for Cert Profile Show testcases")
        print("*" * 80)
        print("MASTER: %s" % master1.hostname)
        print("*" * 80)

        # Export caIPAservice Cert
        master1.kinit_as_admin()
        data = {'host': master1,
                'caIPAserviceCert': '',
                'out': multihost.cacertfile}
        certprofile_run(data)

    def test_0010_positive_cert_profile_show_default(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Successfully show default IPA profile

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        data = {'host': multihost.master,
                'caIPAserviceCert': '',
                'exp_code': '0',
                'op': 'show'}
        certprofile_run(data)

    def test_0011_negative_cert_profile_show_nonexistent(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Fail to show non-existent profile

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated
        """

        # Kinit as admin
        multihost.master.kinit_as_admin()
        data = {'host': multihost.master,
                'testprofile_nonexistent': '',
                'exp_code': '2',
                'op': 'show'}
        certprofile_run(data)

    def test_0012_positive_cert_profile_show_custom(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Successfully show custom profile config

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        # Create a sample configuration
        cname = 'testprofile_custom_profile'
        cname_file = '{}{}.cfg'.format(multihost.tempdir, cname)
        newcname_file = '{}{}_2.cfg'.format(multihost.tempdir, cname)
        export_file = '{}{}_exported.cfg'.format(multihost.tempdir, cname)

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
        data['op'] = 'show'
        certprofile_run(data)
        data['out'] = export_file
        certprofile_run(data)

        cert_data['opfile'] = newcname_file
        create_cert_cfg(cert_data)
        # Cleanup
        data['op'] = 'del'
        certprofile_run(data)

    def class_teardown(self, multihost):
        """ Class teardown for cert_profile_show """
        print("Class teardown for cert_profile_show")
        multihost.master.run_command(['rm', '-rf', multihost.tempdir],
                                     raiseonerr=False)
