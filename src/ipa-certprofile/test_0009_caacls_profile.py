"""
CA ACLs Profile testsuite
"""
import re
import pytest
from datetime import datetime
from lib import certprofile_run, create_cert_cfg, caacl_run
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.qe_class import qe_use_class_setup


class TestCaAclsProfile(object):
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

        print("\nUsing following hosts for CA ACLs Profile testcases")
        print("*" * 80)
        print("MASTER: %s" % master1.hostname)
        print("*" * 80)

        # Export caIPAservice Cert
        master1.kinit_as_admin()
        data = {'host': master1,
                'caIPAserviceCert': '',
                'out': multihost.cacertfile}
        certprofile_run(data)

    def test_0042_positive_caacl_profile_add_profile(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles: Successfully add profile to CA ACL

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
            cfg = re.sub('1.3.6.1.5.5.7.3.1,1.3.6.1.5.5.7.3.2',
                         cnames[cname], cfg)
            multihost.master.put_file_contents(newopfile, cfg)

            data = {'host': multihost.master,
                    cname: '',
                    'store': 'True',
                    'desc': cname + '_cert',
                    'file': newopfile,
                    'exp_code': '0',
                    'op': 'import'}
            certprofile_run(data)

        cname = "testacl_0015"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        caacl_run(data)

        data['certprofiles'] = 'smime'
        data['op'] = 'add-profile'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully
        #             remove profile from CA ACL
        data['op'] = 'remove-profile'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to add
        #             non-existent profile to CA ACL
        cname = "testacl_0015_1"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '0',
                'op': 'add'}
        caacl_run(data)

        data['certprofiles'] = 'smime2'
        data['exp_code'] = '1'
        data['op'] = 'add-profile'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to remove
        #             non-existent profile from CA ACL
        data['op'] = 'remove-profile'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to
        #             add profile to non-existent CA ACL
        cname = "testacl_0015_2"
        data = {'host': multihost.master,
                cname: '',
                'exp_code': '2',
                'certprofiles': 'smime',
                'op': 'add-profile'}
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Fail to
        #             remove profile from non-existent CA ACL
        data['op'] = 'remove-profile'
        caacl_run(data)

        # Delete acl
        data['op'] = 'del'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully add
        #             multiple profiles to CA ACL
        cnames = ['server', 'client']
        del data[cname]

        data['testacl_0016'] = ''
        data['certprofiles'] = cnames
        data['op'] = 'add-profile'
        caacl_run(data)

        # IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully remove
        #             multiple profile from CA ACL
        data['op'] = 'remove-profile'
        caacl_run(data)

        # Delete acl
        data['op'] = 'del'
        caacl_run(data)

        for cname in ['server', 'client', 'smime']:
            data = {'host': multihost.master,
                    cname: '',
                    'exp_code': '0',
                    'op': 'del'}
            certprofile_run(data)

    def class_teardown(self, multihost):
        """ Class teardown for caacls profile """
        multihost.master.run_command(['rm', '-rf', multihost.tempdir],
                                     raiseonerr=False)
