"""
Certprofile Import testsuite
"""
import re
import pytest
from datetime import datetime
from lib import certprofile_run, create_cert_cfg, caacl_run
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.qe_class import qe_use_class_setup


class TestCertProfileImport(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        master1 = multihost.master
        multihost.realm = master1.domain.realm
        now = datetime.now().strftime("%y%m%d_%H%M%S")
        multihost.tempdir = "/tmp/test_%s/" % now
        master1.run_command(['mkdir', '-p', multihost.tempdir], raiseonerr=False)
        multihost.cacertfile = multihost.tempdir + 'caIPAservice.cfg'
        multihost.password = "Secret123"
        multihost.testuser = "testuser1"

        print("\nUsing following hosts for Cert Profile Import testcases")
        print("*" * 80)
        print("MASTER: %s" % master1.hostname)
        print("*" * 80)

        # Export caIPAservice Cert
        master1.kinit_as_admin()
        data = {'host': master1,
                'caIPAserviceCert': '',
                'op': 'show',
                'out': multihost.cacertfile}
        certprofile_run(data)

    def test_0001_positive_cert_profile_import(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Successfully import profile with store in raw config format

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        # Create a sample configuration
        cname = 'testprofile'
        cname_file = '{}{}.cfg'.format(multihost.tempdir, cname)
        cert_data = {'host': multihost.master,
                     'cacert': multihost.cacertfile,
                     'name': cname,
                     'desc': cname + '_cert',
                     'opfile': cname_file}
        create_cert_cfg(cert_data)
        # Import a newly create configuration file
        data = {'host': multihost.master,
                'store': 'True',
                cname: '',
                'desc': cert_data['desc'],
                'file': cert_data['opfile'],
                'exp_code': '0',
                'op': 'import',
                }
        certprofile_run(data)
        data['op'] = 'show'
        certprofile_run(data)

    def test_0002_negative_cert_profile_import(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Fail to import already existing profile with same profileID

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        cname = 'testprofile'
        cname_file = '{}{}.cfg'.format(multihost.tempdir, cname)
        data = {'host': multihost.master,
                'store': 'True',
                cname: '',
                'desc': cname + '_cert',
                'file': cname_file,
                'exp_code': '1',
                'op': 'import'}
        certprofile_run(data)
        # Clean up
        data['exp_code'] = 0
        data['op'] = 'del'
        certprofile_run(data)

    def test_0003_negative_cert_profile_import_xml(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Fail to import profile in xml config format

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        profile_name = 'caUserCert'
        profile_desc = '%s_desc' % profile_name
        profile_file = '{}{}.xml'.format(multihost.tempdir, profile_name)
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['pki', 'cert-request-profile-show',
                                profile_name, '--output', profile_file])
        data = {'host': multihost.master,
                'store': 'True',
                'testprofile_1': '',
                'desc': profile_desc,
                'file': profile_file,
                'exp_code': '1',
                'op': 'import'}
        certprofile_run(data)

    def test_0004_negative_cert_profile_import_classid(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Fail to import profile with classID missing from config

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        cname = 'testprofile_wo_classId'
        opfile = '{}{}.cfg'.format(multihost.tempdir, cname)
        newopfile = '{}{}_2.cfg'.format(multihost.tempdir, cname)
        # Create a sample configuration
        cert_data = {'host': multihost.master,
                     'name': cname,
                     'desc': cname + '_cert',
                     'cacert': multihost.cacertfile,
                     'opfile': opfile}
        create_cert_cfg(cert_data)

        cfg = multihost.master.get_file_contents(opfile)
        cfg = re.sub(r'classId=.*\n?', '', cfg)
        multihost.master.put_file_contents(newopfile, cfg)

        data = {'host': multihost.master,
                'store': 'True',
                cname: '',
                'desc': cname + '_cert',
                'file': newopfile,
                'exp_code': '1',
                'exp_output': 'data did not contain classId attribute.',
                'op': 'import'}
        certprofile_run(data)

    def test_0005_negative_cert_profile_import_profileid(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Fail to import profile with profileID missing from config

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        cname = 'testprofile_with_missing_profileid'
        opfile = '{}{}.cfg'.format(multihost.tempdir, cname)
        newopfile = '{}{}_2.cfg'.format(multihost.tempdir, cname)
        # Create a sample configuration
        cert_data = {'host': multihost.master,
                     'name': cname,
                     'desc': cname + '_cert',
                     'cacert': multihost.cacertfile,
                     'opfile': opfile}
        create_cert_cfg(cert_data)

        cfg = multihost.master.get_file_contents(opfile)
        cfg = re.sub(r'profileId=.*\n?', '', cfg)
        multihost.master.put_file_contents(newopfile, cfg)

        data = {'host': multihost.master,
                'store': 'True',
                cname: '',
                'desc': cname + '_cert',
                'file': newopfile,
                'exp_code': '0',
                'op': 'import',
                }
        certprofile_run(data)
        data['op'] = 'del'
        # Cleanup
        certprofile_run(data)

    def test_0006_cert_profile_import_invalid_profileid(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Fail to import profile with invalid profileID

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        cname = 'testprofile_with_invalid_profileid'
        invalid_cname = 'invalid_' + cname
        opfile = '{}{}.cfg'.format(multihost.tempdir, cname)
        newopfile = '{}{}_2.cfg'.format(multihost.tempdir, cname)
        # Create a sample configuration
        cert_data = {'host': multihost.master,
                     'name': cname,
                     'desc': cname + '_cert',
                     'cacert': multihost.cacertfile,
                     'opfile': opfile}
        create_cert_cfg(cert_data)

        cfg = multihost.master.get_file_contents(opfile)
        cfg = re.sub(r'profileId=.*\n?',
                     'profileId=' + invalid_cname + "\n", cfg)
        multihost.master.put_file_contents(newopfile, cfg)

        data = {'host': multihost.master,
                'store': 'True',
                cname: '',
                'desc': cname + '_cert',
                'file': newopfile,
                'exp_code': '1',
                'exp_output': "Profile ID '" + cname +
                              "' does not match profile data '" +
                              invalid_cname + "'",
                'op': 'import',
                }
        certprofile_run(data)

    def test_0007_positive_cert_profile_import_wo_store(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Successfully import profile without store

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        cname = 'testprofile_wo_store'
        opfile = '{}{}.cfg'.format(multihost.tempdir, cname)
        # Create a sample configuration
        cert_data = {'host': multihost.master,
                     'name': cname,
                     'desc': cname + '_cert',
                     'cacert': multihost.cacertfile,
                     'opfile': opfile}
        create_cert_cfg(cert_data)

        data = {'host': multihost.master,
                cname: '',
                'store': 'False',
                'desc': cname + '_cert',
                'file': opfile,
                'exp_code': '0',
                'op': 'import',
                }
        certprofile_run(data)
        # Cleanup
        data['op'] = 'del'
        certprofile_run(data)

    def test_0008_positive_cert_profile_import_profiles(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Successfully import different types of profiles

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()

        cnames = {'smime': '1.3.6.1.5.5.7.3.4',
                  'server': '1.3.6.1.5.5.7.3.2',
                  'client': '1.3.6.1.5.5.7.3.1'}
        for cname in cnames.keys():
            opfile = '/tmp/' + cname + '.cfg'
            newopfile = '/tmp/' + cname + '_2.cfg'
            # Create a sample configuration
            cert_data = {'host': multihost.master,
                         'name': cname,
                         'desc': cname + '_cert',
                         'cacert': multihost.cacertfile,
                         'opfile': opfile}
            create_cert_cfg(cert_data)
            cfg = multihost.master.get_file_contents(opfile)
            cfg = re.sub('1.3.6.1.5.5.7.3.1,1.3.6.1.5.5.7.3.2',
                         cnames[cname],
                         cfg)
            multihost.master.put_file_contents(newopfile, cfg)

            data = {'host': multihost.master,
                    cname: '',
                    'store': 'True',
                    'desc': cname + '_cert',
                    'file': newopfile,
                    'exp_code': '0',
                    'op': 'import',
                    }
            certprofile_run(data)
            # Cleanup
            data['op'] = 'del'
            certprofile_run(data)

    def test_0009_positive_cert_profile_import_invalid_config(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Fail to import profile with invalid config

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        cnames = {'unknown_classid':
                  ['input.i1.class_id=certReqInputImpl',
                   'input.i1.class_id=certReqInputImplinvalud'],
                  'invalid_list_value':
                  ['policyset.serverCertSet.list=1,2,3,4,5,6,7,8,9,10,11',
                   'policyset.serverCertSet.list=1,2,3,4,5,6,7,8,9,10,11,99']}
        for cname in cnames.keys():
            opfile = '{}{}.cfg'.format(multihost.tempdir, cname)
            newopfile = '{}{}_2.cfg'.format(multihost.tempdir, cname)
            # Create a sample configuration
            cert_data = {'host': multihost.master,
                         'name': cname,
                         'desc': cname + '_cert',
                         'cacert': multihost.cacertfile,
                         'opfile': opfile}
            create_cert_cfg(cert_data)

            cfg = multihost.master.get_file_contents(opfile)
            cfg = re.sub(r'profileId=.*\n?', '', cfg)
            cfg = re.sub(cnames[cname][0], cnames[cname][1], cfg)
            multihost.master.put_file_contents(newopfile, cfg)

            data = {'host': multihost.master,
                    cname: '',
                    'store': 'True',
                    'desc': cname + '_cert',
                    'file': newopfile,
                    'exp_code': '1',
                    'op': 'import'}
            certprofile_run(data)

    def class_teardown(self, multihost):
        """ Class teardown """
        print("Class teardown for Cert profile test suite")
        multihost.master.run_command(['rm', '-rf', multihost.tempdir],
                                     raiseonerr=False)
