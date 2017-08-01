"""
Certprofile Request testsuite
"""
import re
import pytest
from datetime import datetime
from lib import certprofile_run, create_cert_cfg, caacl_run
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.qe_class import qe_use_class_setup


class TestCertProfileRequest(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        master1 = multihost.master
        multihost.replica1 = multihost.replicas[0]
        multihost.realm = master1.domain.realm
        now = datetime.now().strftime("%y%m%d_%H%M%S")
        multihost.tempdir = "/tmp/test_%s/" % now
        master1.run_command(['mkdir', multihost.tempdir], raiseonerr=False)
        multihost.cacertfile = multihost.tempdir + 'caIPAservice.cfg'
        multihost.password = "Secret123"
        multihost.testuser = "testuser1"

        print("\nUsing following hosts for Cert Profile Request testcases")
        print("*" * 80)
        print("MASTER: %s" % master1.hostname)
        print("*" * 80)

        # Export caIPAservice Cert
        master1.kinit_as_admin()
        data = {'host': master1,
                'caIPAserviceCert': '',
                'out': multihost.cacertfile}
        certprofile_run(data)

    def test_0021_positive_cert_request(self, multihost):
        """

        IDM-IPA-TC: Certificate Profiles: Successfully generate cert for user
        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        # Create a sample configuration
        cname = 'userprofile_cert_0021'
        cert_acl = "wide_open_acls_0021"
        cname_file = '{}{}.cfg'.format(multihost.tempdir, cname)
        new_cname_file = '{}{}_2.cfg'.format(multihost.tempdir, cname)
        testuser_csr = "{}{}.csr".format(multihost.tempdir,
                                         multihost.testuser)
        testuser_key = "{}{}.key".format(multihost.tempdir,
                                         multihost.testuser)
        openssl_file = "{}{}.cfg".format(multihost.tempdir,
                                         multihost.testuser)

        cert_data = {'host': multihost.master,
                     'name': cname,
                     'desc': cname + '_cert',
                     'cacert': multihost.cacertfile,
                     'opfile': cname_file}
        create_cert_cfg(cert_data)

        cfg = multihost.master.get_file_contents(cname_file)
        cfg = re.sub('1.3.6.1.5.5.7.3.1,1.3.6.1.5.5.7.3.2',
                     '1.3.6.1.5.5.7.3.4', cfg)
        multihost.master.put_file_contents(new_cname_file, cfg)

        # Import a newly create configuration file
        data = {'host': multihost.master,
                'store': 'True',
                cname: '',
                'desc': cert_data['desc'],
                'file': new_cname_file,
                'exp_code': '0',
                'op': 'import'}
        certprofile_run(data)

        # Add IPA user
        add_ipa_user(multihost.master, multihost.testuser, multihost.password)

        openssl_cfg = "[req]\ndefault_bits = 2048\n" \
                      "distinguished_name = req_distinguished_name\n" \
                      "req_extensions = v3_req\n" \
                      "prompt = no\nencrypt_key = no\n" \
                      "[req_distinguished_name]\n" \
                      "commonName = %s\n" \
                      "[ v3_req ]\n" \
                      "subjectAltName = email:" \
                      "%s@%s" % (multihost.testuser,
                                 multihost.testuser,
                                 multihost.master.domain.name)

        multihost.master.put_file_contents(openssl_file, openssl_cfg)
        multihost.master.qerun(['openssl', 'req', '-out', testuser_csr,
                                '-new', '-newkey', 'rsa:2048', '-nodes',
                                '-keyout', testuser_key,
                                '-config', openssl_file],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'caacl-add', '--profilecat=all',
                                cert_acl, '--usercat=all', '--hostcat=all',
                                '--servicecat=all'],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'cert-request', testuser_csr,
                                '--profile-id=' + cname,
                                '--principal=%s' % multihost.testuser],
                               exp_returncode=0)
        data['op'] = 'del'
        certprofile_run(data)
        multihost.master.qerun(['ipa', 'user-del', multihost.testuser],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'caacl-del', cert_acl])

    def test_0022_positive_cert_request_multiple_email(self, multihost):
        """

        IDM-IPA-TC: Certificate Profiles: Successfully generate cert for user
                        when SNA includes multiple email
        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        # Add IPA user
        multihost.testuser = 'testuser2'
        # Create a sample configuration
        cname = 'userprofile_cert_0022'
        cname_file = '{}{}.cfg'.format(multihost.tempdir, cname)
        new_cname_file = '{}{}_2.cfg'.format(multihost.tempdir, cname)
        email2 = "tu2@example.com"
        email1 = "%s@example.com" % (multihost.testuser)
        cert_acl = "wide_open_acls_0022"
        testuser_csr = "{}{}.csr".format(multihost.tempdir, multihost.testuser)
        testuser_key = "{}{}.key".format(multihost.tempdir, multihost.testuser)
        openssl_file = "{}{}.cfg".format(multihost.tempdir, multihost.testuser)

        add_ipa_user(multihost.master, multihost.testuser, multihost.password)

        multihost.master.qerun(['ipa', 'user-mod', multihost.testuser,
                                '--email=' + email1, '--email=' + email2])
        multihost.master.qerun(['ipa', 'user-show', multihost.testuser])

        cert_data = {'host': multihost.master,
                     'name': cname,
                     'desc': cname + '_cert',
                     'cacert': multihost.cacertfile,
                     'opfile': cname_file}
        create_cert_cfg(cert_data)

        cfg = multihost.master.get_file_contents(cname_file)
        cfg = re.sub('1.3.6.1.5.5.7.3.1,1.3.6.1.5.5.7.3.2',
                     '1.3.6.1.5.5.7.3.4', cfg)
        cfg = re.sub(r'profileId=.*\n?', '', cfg)
        multihost.master.put_file_contents(new_cname_file, cfg)

        # Import a newly create configuration file
        data = {'host': multihost.master,
                'store': 'True',
                cname: '',
                'desc': cert_data['desc'],
                'file': new_cname_file,
                'exp_code': '0',
                'op': 'import'}
        certprofile_run(data)

        openssl_cfg = "[req]\ndefault_bits = 2048\n" \
                      "distinguished_name = req_distinguished_name\n" \
                      "req_extensions = v3_req\n" \
                      "prompt = no\nencrypt_key = no\n" \
                      "[req_distinguished_name]\n" \
                      "commonName = %s\n[ v3_req ]\n" \
                      "subjectAltName = " \
                      "email:%s,email:%s" % (multihost.testuser,
                                             email1,
                                             email2)

        multihost.master.put_file_contents(openssl_file, openssl_cfg)
        multihost.master.qerun(['openssl', 'req', '-out', testuser_csr,
                                '-new', '-newkey', 'rsa:2048', '-nodes',
                                '-keyout', testuser_key,
                                '-config', openssl_file],
                               exp_returncode=0)

        multihost.master.qerun(['ipa', 'caacl-add', '--profilecat=all',
                                cert_acl, '--usercat=all', '--hostcat=all',
                                '--servicecat=all'],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'cert-request', testuser_csr,
                                '--profile-id=' + cname,
                                '--principal=%s' % multihost.testuser],
                               exp_returncode=0)
        data['op'] = 'del'
        certprofile_run(data)
        multihost.master.qerun(['ipa', 'user-del', multihost.testuser],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'caacl-del', cert_acl])

    def test_0023_negative_cert_request_invalid_email(self, multihost):
        """

        IDM-IPA-TC: Certificate Profiles: Fail to generate cert for user
                when subjectAltName email invalid
        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        # Create a sample configuration

        cname = 'userprofile_cert_0023'
        multihost.testuser = "testuser3"
        cname_file = '{}{}.cfg'.format(multihost.tempdir, cname)
        new_cname_file = '{}{}_2.cfg'.format(multihost.tempdir, cname)
        testuser_csr = "{}{}.csr".format(multihost.tempdir, multihost.testuser)
        testuser_key = "{}{}.key".format(multihost.tempdir, multihost.testuser)
        openssl_file = "{}{}.cfg".format(multihost.tempdir, multihost.testuser)
        cert_acl = "wide_open_acls_0023"
        invalid_email = "%s@fake.com" % (multihost.testuser)

        cert_data = {'host': multihost.master,
                     'name': cname,
                     'desc': cname + '_cert',
                     'cacert': multihost.cacertfile,
                     'opfile': cname_file}
        create_cert_cfg(cert_data)

        cfg = multihost.master.get_file_contents(cname_file)
        cfg = re.sub('1.3.6.1.5.5.7.3.1,1.3.6.1.5.5.7.3.2',
                     '1.3.6.1.5.5.7.3.4', cfg)
        multihost.master.put_file_contents(new_cname_file, cfg)

        # Import a newly create configuration file
        data = {'host': multihost.master,
                'store': 'True',
                cname: '',
                'desc': cert_data['desc'],
                'file': new_cname_file,
                'exp_code': '0',
                'op': 'import'}
        certprofile_run(data)

        # Add IPA user
        add_ipa_user(multihost.master, multihost.testuser, multihost.password)

        openssl_cfg = "[req]\n" \
                      "default_bits = 2048\n" \
                      "distinguished_name = req_distinguished_name\n" \
                      "req_extensions = v3_req\n" \
                      "prompt = no\nencrypt_key = no\n" \
                      "[req_distinguished_name]\n" \
                      "commonName = %s\n[ v3_req ]\n" \
                      "subjectAltName = " \
                      "email: %s" % (multihost.testuser,
                                     invalid_email)

        multihost.master.put_file_contents(openssl_file, openssl_cfg)
        multihost.master.qerun(['openssl', 'req', '-out', testuser_csr,
                                '-new', '-newkey', 'rsa:2048', '-nodes',
                                '-keyout', testuser_key,
                                '-config', openssl_file],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'caacl-add', '--profilecat=all',
                                cert_acl, '--usercat=all', '--hostcat=all',
                                '--servicecat=all'],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'cert-request', testuser_csr,
                                '--profile-id=' + cname,
                                '--principal=%s' % (multihost.testuser)],
                               exp_returncode=1)
        data['op'] = 'del'
        certprofile_run(data)
        multihost.master.qerun(['ipa', 'user-del', multihost.testuser],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'caacl-del', cert_acl])

    def test_0024_negative_cert_request_domain_name(self, multihost):
        """

        IDM-IPA-TC: Certificate Profiles: Fail to generate cert for
                user when subjectAltName includes DNS
        """
        # Kinit as admin
        multihost.master.kinit_as_admin()

        # Create a sample configuration
        cname = 'userprofile_cert_0024'
        multihost.testuser = "testuser4"
        cname_file = '{}{}.cfg'.format(multihost.tempdir, cname)
        new_cname_file = '{}{}_2.cfg'.format(multihost.tempdir, cname)
        testuser_csr = "{}{}.csr".format(multihost.tempdir, multihost.testuser)
        testuser_key = "{}{}.key".format(multihost.tempdir, multihost.testuser)
        openssl_file = "{}{}.cfg".format(multihost.tempdir, multihost.testuser)
        cert_acl = "wide_open_acls_0024"
        # This is fake value
        invalid_dns = "dhcp201-131.testrelm.test"

        cert_data = {'host': multihost.master,
                     'name': cname,
                     'desc': cname + '_cert',
                     'cacert': multihost.cacertfile,
                     'opfile': cname_file}
        create_cert_cfg(cert_data)

        cfg = multihost.master.get_file_contents(cname_file)
        cfg = re.sub('1.3.6.1.5.5.7.3.1,1.3.6.1.5.5.7.3.2',
                     '1.3.6.1.5.5.7.3.4', cfg)
        multihost.master.put_file_contents(new_cname_file, cfg)

        # Import a newly create configuration file
        data = {'host': multihost.master,
                'store': 'True',
                cname: '',
                'desc': cert_data['desc'],
                'file': new_cname_file,
                'exp_code': '0',
                'op': 'import'}
        certprofile_run(data)

        # Add IPA user
        add_ipa_user(multihost.master, multihost.testuser, multihost.password)

        openssl_cfg = "[req]\n" \
                      "default_bits = 2048\n" \
                      "distinguished_name = req_distinguished_name\n" \
                      "req_extensions = v3_req\n" \
                      "prompt = no\nencrypt_key = no\n" \
                      "[req_distinguished_name]\n" \
                      "commonName = %s\n[ v3_req ]\n" \
                      "subjectAltName = DNS:" \
                      "%s" % (multihost.testuser, invalid_dns)

        multihost.master.put_file_contents(openssl_file, openssl_cfg)
        multihost.master.qerun(['openssl', 'req', '-out', testuser_csr,
                                '-new', '-newkey', 'rsa:2048', '-nodes',
                                '-keyout', testuser_key,
                                '-config', openssl_file],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'caacl-add', '--profilecat=all',
                                cert_acl, '--usercat=all', '--hostcat=all',
                                '--servicecat=all'],
                               exp_returncode=0)
        output = "subject alt name type DNSName is forbidden " \
                 "for user principals"
        multihost.master.qerun(['ipa', 'cert-request', testuser_csr,
                                '--profile-id=' + cname,
                                '--principal=%s' % multihost.testuser],
                               exp_returncode=1,
                               exp_output=output)
        # Cleanup
        data['op'] = 'del'
        certprofile_run(data)
        multihost.master.qerun(['ipa', 'user-del', multihost.testuser],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'caacl-del', cert_acl])

    def test_0025_positive_cert_request_replica_ldap(self, multihost):
        """

        IDM-IPA-TC: Certificate Profiles: Successfully see imported
                profile is replicated
        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        # Create a sample configuration
        cname = 'userprofile_cert_0025'
        cname_file = '{}{}.cfg'.format(multihost.tempdir, cname)
        new_cname_file = '{}{}_2.cfg'.format(multihost.tempdir, cname)

        cert_data = {'host': multihost.master,
                     'name': cname,
                     'desc': cname + '_cert',
                     'cacert': multihost.cacertfile,
                     'opfile': cname_file}
        create_cert_cfg(cert_data)

        cfg = multihost.master.get_file_contents(cname_file)
        cfg = re.sub('1.3.6.1.5.5.7.3.1,1.3.6.1.5.5.7.3.2',
                     '1.3.6.1.5.5.7.3.4', cfg)
        multihost.master.put_file_contents(new_cname_file, cfg)

        # Import a newly create configuration file
        data = {'host': multihost.master,
                'store': 'True',
                cname: '',
                'desc': cert_data['desc'],
                'file': new_cname_file,
                'exp_code': '0',
                'op': 'import'}
        certprofile_run(data)
        search = ['ldapsearch', '-xLLL',
                  '-D', 'cn=Directory Manager',
                  '-w', 'Secret123',
                  '-h', multihost.master.hostname,
                  '-b', 'ou=certificateProfiles,ou=ca,o=ipaca']
        cmd = multihost.replica1.run_command(search, raiseonerr=True)
        if cmd.returncode != 0:
            pytest.fail("Fail to verify")
        data['op'] = 'del'
        certprofile_run(data)

    def test_0026_positive_cert_request_replica_delete(self, multihost):
        """

        IDM-IPA-TC: Certificate Profiles: Successfully see deleted profile
                is removed from all replicas
        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        # Create a sample configuration
        cname = 'userprofile_cert_0026'
        cname_file = '{}{}.cfg'.format(multihost.tempdir, cname)
        new_cname_file = '{}{}_2.cfg'.format(multihost.tempdir, cname)

        cert_data = {'host': multihost.master,
                     'name': cname,
                     'desc': cname + '_cert',
                     'cacert': multihost.cacertfile,
                     'opfile': cname_file}
        create_cert_cfg(cert_data)

        cfg = multihost.master.get_file_contents(cname_file)
        cfg = re.sub('1.3.6.1.5.5.7.3.1,1.3.6.1.5.5.7.3.2',
                     '1.3.6.1.5.5.7.3.4', cfg)
        multihost.master.put_file_contents(new_cname_file, cfg)

        # Import a newly create configuration file
        data = {'host': multihost.master,
                'store': 'True',
                cname: '',
                'desc': cert_data['desc'],
                'file': new_cname_file,
                'exp_code': '0',
                'op': 'import'}
        certprofile_run(data)
        search = ['ldapsearch', '-xLLL',
                  '-D', 'cn=Directory Manager',
                  '-w', 'Secret123',
                  '-h', multihost.master.hostname,
                  '-b', '"ou=certificateProfiles,ou=ca,o=ipaca"']
        multihost.replica1.qerun(search, exp_returncode=32)

        data['host'] = multihost.master
        data['op'] = 'del'
        certprofile_run(data)

    def test_0027_positive_cert_request_krb5principal_name(self, multihost):
        """

        IDM-IPA-TC: Certificate Profiles: Successfully request cert with
                krb5principalName SAN
        """
        # Kinit as admin
        multihost.master.kinit_as_admin()
        # Create a sample configuration

        cname = 'userprofile_cert_0027'
        multihost.testuser = "testuser5"
        cname_file = '{}{}.cfg'.format(multihost.tempdir, cname)
        new_cname_file = '{}{}_2.cfg'.format(multihost.tempdir, cname)
        testuser_csr = "{}{}.csr".format(multihost.tempdir, multihost.testuser)
        testuser_key = "{}{}.key".format(multihost.tempdir, multihost.testuser)
        openssl_file = "{}{}.cfg".format(multihost.tempdir, multihost.testuser)
        cert_acl = "wide_open_acls_0025"
        subjectAltName = "otherName:1.3.6.1.5.2.2;SEQUENCE:krb5principal"

        cert_data = {'host': multihost.master,
                     'name': cname,
                     'desc': cname + '_cert',
                     'cacert': multihost.cacertfile,
                     'opfile': cname_file}
        create_cert_cfg(cert_data)

        cfg = multihost.master.get_file_contents(cname_file)
        cfg = re.sub('1.3.6.1.5.5.7.3.1,1.3.6.1.5.5.7.3.2',
                     '1.3.6.1.5.5.7.3.4', cfg)
        multihost.master.put_file_contents(new_cname_file, cfg)

        # Import a newly create configuration file
        data = {'host': multihost.master,
                'store': 'True',
                cname: '',
                'desc': cert_data['desc'],
                'file': new_cname_file,
                'exp_code': '0',
                'op': 'import'}
        certprofile_run(data)

        # Add IPA user
        add_ipa_user(multihost.master, multihost.testuser, multihost.password)

        openssl_cfg = "[req]\n"\
                      "default_bits = 2048\n" \
                      "distinguished_name = dn\n" \
                      "req_extensions = exts\n" \
                      "prompt = no\n" \
                      "encrypt_key = no\n" \
                      "[dn]\n" \
                      "commonName = %s\n" \
                      "[exts]\n" \
                      "subjectAltName = %s\n" \
                      "[ krb5principal ]\n" \
                      "realm = EXPLICIT:0,GeneralString:%s\n" \
                      "principalname = EXPLICIT:1,SEQUENCE:principalname\n" \
                      "[ principalname ]\n" \
                      "nametype = EXPLICIT:0,INT:0\n" \
                      "namestring = EXPLICIT:1,SEQUENCE:namestring\n" \
                      "[ namestring ]\n" \
                      "part1 = " \
                      "GeneralString:%s\n" % (multihost.testuser,
                                              subjectAltName,
                                              multihost.master.domain.realm,
                                              multihost.testuser)

        multihost.master.put_file_contents(openssl_file, openssl_cfg)
        multihost.master.qerun(['openssl', 'req', '-out', testuser_csr,
                                '-new', '-newkey', 'rsa:2048', '-nodes',
                                '-keyout', testuser_key,
                                '-config', openssl_file],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'caacl-add', '--profilecat=all',
                                cert_acl, '--usercat=all', '--hostcat=all',
                                '--servicecat=all'],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'cert-request', testuser_csr,
                                '--profile-id=' + cname,
                                '--principal=%s' % (multihost.testuser)],
                               exp_returncode=0)
        data['op'] = 'del'
        certprofile_run(data)
        multihost.master.qerun(['ipa', 'user-del', multihost.testuser],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'caacl-del', cert_acl])

    def test_bz1364197_request_svc_cert_as_svc(self, multihost):
        """
        @Title: IPA-IDM-TC: Certificate Profiles: Request service certificate as service
        """
        master1 = multihost.master
        cpname = 'bz1364197_cert_profile'
        caacl = 'bz1364197_caacl'
        bzprofile_cfg = multihost.tempdir + 'bz1364197_profile.cfg'
        bzhost = {}
        domain = multihost.master.domain.name
        openssl_file = multihost.tempdir + 'bz1364197_openssl.cfg'
        service_csr = multihost.tempdir + 'bz1364197_openssl.csr'
        keytab_file = multihost.tempdir + 'bz1364197_service2.keytab'

        # Kinit as admin
        master1.kinit_as_admin()

        # Add reverse dnszone for test hosts
        master1.qerun(['ipa', 'dnszone-add', '73.168.192.in-addr.arpa.',
                       '--skip-overlap-check'])

        # Add hosts 1 and 2 and services 1 and 2
        for i in [1, 2]:
            bzhost[i] = {'name': 'bz1364197-master{}.{}'.format(i, domain),
                         'ip': '192.168.73.20{}'.format(i)}
            master1.qerun(['ipa', 'host-add', bzhost[i]['name'],
                           '--ip-address', bzhost[i]['ip']])
            master1.qerun(['ipa', 'service-add',
                           'svc/{}'.format(bzhost[i]['name'])])

        # add host2 to manage service1
        master1.qerun(['ipa', 'service-add-host',
                       'svc/{}'.format(bzhost[1]['name']),
                       '--hosts', bzhost[2]['name']])

        # Get template config from default profile
        data = {'host': master1,
                'caIPAserviceCert': '',
                'out': bzprofile_cfg}
        certprofile_run(data)

        # Create cert profile config file
        cert_data = {'host': master1,
                     'name': cpname,
                     'desc': cpname + '_cert',
                     'cacert': bzprofile_cfg,
                     'opfile': bzprofile_cfg}
        create_cert_cfg(cert_data)

        # Import a newly create profile config file
        data = {'host': master1,
                'store': 'True',
                cpname: '',
                'desc': cert_data['desc'],
                'file': bzprofile_cfg,
                'exp_code': '0',
                'op': 'import'}
        certprofile_run(data)

        # Create CAACL for profile
        master1.qerun(['ipa', 'caacl-add', caacl])
        master1.qerun(['ipa', 'caacl-add-ca', caacl,
                       '--cas', 'ipa'])
        master1.qerun(['ipa', 'caacl-add-profile', caacl,
                       '--certprofiles', cpname])
        master1.qerun(['ipa', 'caacl-add-host', caacl,
                       '--hosts', bzhost[2]['name']])
        master1.qerun(['ipa', 'caacl-add-service', caacl,
                       '--services', 'svc/' + bzhost[2]['name'],
                       '--services', 'svc/' + bzhost[1]['name']])

        # Create config for cert request
        openssl_cfg = "[req]\n" \
                      "default_bits = 2048\n" \
                      "distinguished_name = req_distinguished_name\n" \
                      "req_extensions = v3_req\n" \
                      "prompt = no\nencrypt_key = no\n" \
                      "[req_distinguished_name]\n" \
                      "commonName = %s\n" \
                      "[ v3_req ]\n" \
                      "basicConstraints = CA:FALSE\n" \
                      "keyUsage = nonRepudiation, digitalSignature, keyEncipherment\n" \
                      "subjectAltName = @alt_names\n" \
                      "[alt_names]\n" \
                      "DNS.1 = %s\n" \
                      "DNS.2 = %s\n" % (bzhost[2]['name'],
                                        bzhost[2]['name'],
                                        bzhost[1]['name'])
        master1.put_file_contents(openssl_file, openssl_cfg)

        # Create CSR with openssl
        master1.qerun(['openssl', 'req', '-out', service_csr,
                       '-new', '-nodes', '-config', openssl_file])

        # Get keytab and kinit as host2
        master1.qerun(['ipa-getkeytab', '-p', 'host/' + bzhost[2]['name'],
                       '-k', keytab_file])
        master1.qerun(['kinit', '-kt', keytab_file,
                       'host/' + bzhost[2]['name']])

        # Submit CSR to IPA as service2
        master1.qerun(['ipa', 'cert-request', service_csr,
                       '--profile-id', cpname,
                       '--principal', 'svc/' + bzhost[2]['name']])

        master1.kinit_as_admin()
        master1.qerun(['ipa', 'caacl-del', caacl])
        for i in [1, 2]:
            master1.qerun(['ipa', 'service-del', 'svc/' + bzhost[i]['name']])
            master1.qerun(['ipa', 'host-del', bzhost[i]['name'], '--updatedns'])
        master1.qerun(['ipa', 'dnszone-del', '73.168.192.in-addr.arpa.'])
        data['op'] = 'del'
        certprofile_run(data)

    def class_teardown(self, multihost):
        """ class teardown for Cert Profile Request """
        print("Running tear down for cert profile request")
        multihost.master.run_command(['rm', '-rf', multihost.tempdir],
                                     raiseonerr=False)
