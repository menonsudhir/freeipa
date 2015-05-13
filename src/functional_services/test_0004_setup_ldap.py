"""
Functional Services LDAP Setup including certificate and service setup.
"""

import pytest
import re
import requests
import socket
from ipa_pytests.shared.utils import ldapmodify
from ipa_pytests.shared.utils import add_ipa_user
from ipa_pytests.shared.qe_certutils import certutil


class TestSetupLdap(object):
    """ FS Setup LDAP class """
    def class_setup(self, multihost):
        """ class setup """
        pass

    @pytest.mark.tier1
    def test_0001_add_ldap_user(self, multihost):
        """ Add IPA user for ldap """
        add_ipa_user(multihost.master, "ldapuser1")

    @pytest.mark.tier1
    def test_0002_add_ldap_services(self, multihost):
        """ Add IPA service for ldap """
        multihost.master.kinit_as_admin()
        multihost.master.run_command(['ipa', 'service-add', 'ldap/' + multihost.client.hostname])

    @pytest.mark.tier1
    def test_0003_get_ldap_keytab(self, multihost):
        """ Get keytab for ldap """
        multihost.client.kinit_as_admin()
        multihost.client.run_command(['ipa-getkeytab', '-s', multihost.master.hostname,
                                      '-k', '/etc/dirsrv/ldap_service.keytab',
                                      '-p', 'ldap/' + multihost.client.hostname])
        multihost.client.run_command(['chown', 'nobody.nobody',
                                      '/etc/dirsrv/ldap_service.keytab'])
        multihost.client.run_command(['chmod', '0400',
                                      '/etc/dirsrv/ldap_service.keytab'])

    @pytest.mark.tier1
    def test_0004_initialize_ldap_instance(self, multihost):
        """ Initialize ldap server instance """
        cfgget = '/opt/ipa_pytests/functional_services/ldap-instance.inf'
        cfgput = '/tmp/ldap-instance.inf'
        multihost.client.run_command(['rm', '-rf', cfgput])
        ldapcfg = multihost.client.get_file_contents(cfgget)
        ldapcfg = re.sub('MY_VAR_CLIENT', multihost.client.hostname, ldapcfg)
        ldapcfg = re.sub('MY_VAR_PORT', '3389', ldapcfg)
        multihost.client.put_file_contents(cfgput, ldapcfg)
        multihost.client.run_command(['/usr/sbin/setup-ds.pl', '--silent',
                                      '--file=' + cfgput])

    @pytest.mark.tier1
    def test_0005_set_ldap_password_scheme(self, multihost):
        """ Configure ldap password scheme """
        uri = 'ldap://' + multihost.client.hostname + ':3389'
        username = 'cn=Directory Manager'
        password = 'Secret123'
        ldif_file = '/opt/ipa_pytests/functional_services/ldap-pwscheme.ldif'
        ldapmodify(uri, username, password, ldif_file)

    @pytest.mark.tier1
    def test_0006_set_ldap_sasl(self, multihost):
        """ Configure ldap sasl """
        uri = 'ldap://' + multihost.client.hostname + ':3389'
        username = 'cn=Directory Manager'
        password = 'Secret123'
        ldif_file = '/opt/ipa_pytests/functional_services/ldap-sasl.ldif'
        ldapmodify(uri, username, password, ldif_file)

    @pytest.mark.tier1
    def test_0007_set_krb_keytab(self, multihost):
        """ Configure ldap to point to keytab """
        cfgget = '/etc/sysconfig/dirsrv'
        cfgput = '/etc/sysconfig/dirsrv'
        ldapcfg = multihost.client.get_file_contents(cfgget)
        ldapcfg = ldapcfg + '\nKRB5_KTNAME=/etc/dirsrv/ldap_service.keytab ; export KRB5_KTNAME\n'
        multihost.client.put_file_contents(cfgput, ldapcfg)
        multihost.client.run_command(['service', 'dirsrv', 'restart'])

    @pytest.mark.tier1
    def test_0008_add_user_to_ldap(self, multihost):
        """ Add ldap user in ldap """
        uri = 'ldap://' + multihost.client.hostname + ':3389'
        username = 'cn=Directory Manager'
        password = 'Secret123'
        ldif_file = '/opt/ipa_pytests/functional_services/ldap-user.ldif'
        ldapmodify(uri, username, password, ldif_file)

    @pytest.mark.tier1
    def test_0009_add_ipa_ca_cert_to_ldap(self, multihost):
        """ Add IPA CA certificate to ldap """
        crtget = "http://" + multihost.master.hostname + "/ipa/config/ca.crt"
        crtput = "/etc/dirsrv/slapd-instance1/ca.crt"
        ldap_cert_db = "/etc/dirsrv/slapd-instance1"
        nick = "IPA CA"
        trust = "CT,,"
        crtdata = requests.get(crtget).text
        multihost.client.put_file_contents(crtput, crtdata)
        mycerts = certutil(multihost.client, ldap_cert_db)
        mycerts.add_cert(crtput, nick, trust)

    @pytest.mark.tier1
    def test_0010_get_cert_for_ldap_service(self, multihost):
        """ Create certificate for ldap service """
        suffix = ""
        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa', 'config-show', '--raw'])
        for line in cmd.stdout_text.split('\n'):
            if "ipacertificatesubjectbase" in line:
                suffix = line.split()[1]
        if suffix == "":
            suffix = "O=" + multihost.master.domain.realm
        subject = "CN=" + multihost.client.hostname + "," + suffix
        ldap_cert_db = "/etc/dirsrv/slapd-instance1"
        nick = multihost.client.hostname
        trust = "u,u,u"
        csr_file = "/tmp/ldap-func-services.csr"
        crt_file = "/tmp/ldap-func-services.crt"
        mycerts = certutil(multihost.client, ldap_cert_db)
        mycerts.request_cert(subject, csr_file)
        multihost.client.run_command(['ipa', 'cert-request',
                                      '--principal=ldap/' + multihost.client.hostname,
                                      csr_file])
        multihost.client.run_command(['ipa', 'service-show',
                                      'ldap/' + multihost.client.hostname,
                                      '--out=' + crt_file])
        mycerts.add_cert(crt_file, nick, trust)
        mycerts.verify_cert(nick)

    @pytest.mark.tier1
    def test_0011_enable_ssl_for_ldap(self, multihost):
        """ Configure ldap to enable ssl """
        myself = multihost.config.host_by_name(socket.gethostname())
        uri = 'ldap://' + multihost.client.hostname + ':3389'
        username = 'cn=Directory Manager'
        password = 'Secret123'
        ldif_get = '/opt/ipa_pytests/functional_services/ldap-enablessl.ldif'
        ldif_put = '/tmp/mytest-ldap-enablessl.ldif'
        ldapcfg = myself.get_file_contents(ldif_get)
        ldapcfg = re.sub('MY_VAR_CLIENT', multihost.client.hostname, ldapcfg)
        ldapcfg = re.sub('MY_VAR_SECURE_PORT', '6636', ldapcfg)
        # must put to master here because that's where ldapmodify is run from
        myself.put_file_contents(ldif_put, ldapcfg)
        ldapmodify(uri, username, password, ldif_put)
        pin = "Internal (Software) Token:Secret123"
        pin_file = "/etc/dirsrv/slapd-instance1/pin.txt"
        multihost.client.put_file_contents(pin_file, pin)
        multihost.client.run_command(['semanage', 'port', '-a', '-t', 'ldap_port_t',
                                      '-p', 'tcp', '6636'], raiseonerr=False)
        multihost.client.run_command(['service', 'dirsrv', 'restart'])

    def class_teardown(self, multihost):
        """ class teardown """
        pass
