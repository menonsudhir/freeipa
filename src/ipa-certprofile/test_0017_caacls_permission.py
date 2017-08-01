"""
CA ACLs permissions testsuite
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
        master1.run_command(['mkdir', multihost.tempdir], raiseonerr=False)
        multihost.cacertfile = multihost.tempdir + 'caIPAservice.cfg'
        multihost.password = "Secret123"
        multihost.testuser = "testuser1"

        print("\nUsing following hosts for CA ACLs Permission testcases")
        print("*" * 80)
        print("MASTER: %s" % master1.hostname)
        print("*" * 80)

        # Export caIPAservice Cert
        master1.kinit_as_admin()
        data = {'host': master1,
                'caIPAserviceCert': '',
                'out': multihost.cacertfile}
        certprofile_run(data)

    def test_0061_caacls_permission_acls(self, multihost):
        """

        :Title: IDM-IPA-TC: Certificate Profiles CA ACLs: Successfully run cert-request with CAACL ignore permission

        :Requirement: IDM-IPA-REQ : Cert Profile

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # Kdestroy
        multihost.master.qerun(['kdestroy', '-A'])
        # Kinit as admin
        multihost.master.kinit_as_admin()
        # create a new CA ACL
        cname = 'testacl_0061'
        testuser = "testuser_0061"
        testpriv = "testpriv_0061"
        testuser_csr = "{}{}.csr".format(multihost.tempdir, testuser)
        testuser_key = "{}{}.key".format(multihost.tempdir, testuser)
        openssl_file = "{}{}.cfg".format(multihost.tempdir, testuser)
        testrole = "testrole_0061"
        testgroup = "testgroup_0061"

        caacl_data = {'host': multihost.master,
                      cname: '',
                      'exp_code': '0',
                      'op': 'add'}
        caacl_run(caacl_data)
        add_ipa_user(multihost.master, testuser, multihost.password)
        multihost.master.qerun(['ipa', 'privilege-add', testpriv],
                               exp_returncode=0)
        permlsts = ['--permissions=Request Certificate ignoring CA ACLs',
                    '--permissions=Request Certificate',
                    '--permissions=Request Certificates from a different host',
                    '--permissions=Get Certificates status from the CA',
                    '--permissions=Revoke Certificate',
                    '--permissions=Certificate Remove Hold',
                    '--permissions=System: Add CA Certificate For Renewal',
                    '--permissions=System: Add Certificate Store Entry',
                    '--permissions=System: Modify CA Certificate',
                    '--permissions=System: Modify CA Certificate For Renewal',
                    '--permissions=System: Modify Certificate Store Entry',
                    '--permissions=System: Remove Certificate Store Entry']
        for permlist in permlsts:
            multihost.master.qerun(['ipa', 'privilege-add-permission',
                                    testpriv, permlist], exp_returncode=0)

        multihost.master.qerun(['ipa', 'role-add', testrole],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'role-add-privilege', testrole,
                                '--privileges=%s' % testpriv],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'group-add', testgroup],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'role-add-member', testrole,
                                '--groups=%s' % testgroup],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'group-add-member', testgroup,
                                '--users=%s' % testuser],
                               exp_returncode=0)

        cname = 'caIPAuserCert'
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

        cert_profile_data = {'host': multihost.master,
                             'store': 'True',
                             cname: '',
                             'desc': cname + '_cert',
                             'file': newopfile,
                             'exp_code': '0',
                             'op': 'import'}
        certprofile_run(cert_profile_data)

        cmd = multihost.master.run_command(['kinit', testuser],
                                           stdin_text=multihost.password)
        if cmd.returncode != 0:
            pytest.xfail("Failed to login as user [%s] " % testuser)

        openssl_cfg = "[req]\n" \
                      "default_bits = 2048\n" \
                      "distinguished_name = rdn\n" \
                      "req_extensions = v3_req\n" \
                      "prompt = no\n" \
                      "encrypt_key = no\n" \
                      "[rdn]\n" \
                      "commonName = %s\n[ v3_req ]\n" \
                      "subjectAltName = email:" \
                      "%s@%s" % (testuser,
                                 testuser,
                                 multihost.master.domain.name)

        multihost.master.put_file_contents(openssl_file, openssl_cfg)
        multihost.master.qerun(['openssl', 'req',
                                '-out', testuser_csr,
                                '-new', '-newkey', 'rsa:2048', '-nodes',
                                '-keyout', testuser_key,
                                '-config', openssl_file],
                               exp_returncode=0)

        multihost.master.qerun(['ipa', 'cert-request', testuser_csr,
                                '--profile-id=%s' % cname,
                                '--principal=%s' % testuser],
                               exp_returncode=0)

        # Clean up
        # Kinit as admin
        multihost.master.kinit_as_admin()
        caacl_data['op'] = 'del'
        caacl_run(caacl_data)
        multihost.master.qerun(['ipa', 'user-del', testuser],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'privilege-del', testpriv],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'role-del', testrole],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'group-del', testgroup],
                               exp_returncode=0)
        for tempfile in [testuser_csr, testuser_key, openssl_file]:
            multihost.master.qerun(['rm', '-rf', tempfile], exp_returncode=0)
        cert_profile_data['op'] = 'del'
        certprofile_run(cert_profile_data)

    def class_teardown(self, multihost):
        """ Class teardown for caacls permission """
        multihost.master.run_command(['rm', '-rf', multihost.tempdir],
                                     raiseonerr=False)
