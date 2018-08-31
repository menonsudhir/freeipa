"""
Functional Services LDAP Access Tests
"""

import re
import pytest
from .setup_lib_ldap import setup_ldap_service
from .support import ldap_sasl_check_positive
from .support import ldap_sasl_check_negative
from .support import ldap_simple_bind_check_positve
from .support import is_redundant_ca_dns_supported
from .support import check_revoked


class TestLdap(object):
    """ FS LDAP Tests class """
    def class_setup(self, multihost):
        """ IPA-TC: Functional Services: Setup LDAP Service software and requirements for test """
        fin = '/tmp/ipa_func_svcs_setup_ldap_service_done'
        if not multihost.client.transport.file_exists(fin):
            setup_ldap_service(multihost)
            multihost.client.put_file_contents(fin, 'x')
        else:
            print("setup_ldap_service has already run...skipping")

    @pytest.mark.tier1
    def test_0001_access_ldap_with_creds(self, multihost):
        """ IPA-TC: Functional Services: Access ldap with valid credentials """
        multihost.master.kinit_as_user('ldapuser1', 'Secret123')
        ldap_sasl_check_positive(multihost.master, 'ldap://' + multihost.client.hostname + ':3389')

    @pytest.mark.tier1
    def test_0002_deny_ldap_without_creds(self, multihost):
        """ IPA-TC: Functional Services: deny access to ldap without valid credentials """
        multihost.master.qerun(['kdestroy', '-A'])
        ldap_sasl_check_negative(multihost.master, 'ldap://' + multihost.client.hostname + ':3389',
                                 'Credentials cache file.*not found|No Kerberos credentials available')

    @pytest.mark.tier1
    def test_0003_access_ldaps_with_creds(self, multihost):
        """ IPA-TC: Functional Services: Access ldaps with valid credentials """
        multihost.master.kinit_as_user('ldapuser1', 'Secret123')
        ldap_sasl_check_positive(multihost.master, 'ldaps://' + multihost.client.hostname + ':6636')

    @pytest.mark.tier1
    def test_0004_deny_ldaps_without_creds(self, multihost):
        """ IPA-TC: Functional Services: deny access to ldaps without valid credentials """
        multihost.master.qerun(['kdestroy', '-A'])
        ldap_sasl_check_negative(multihost.master, 'ldaps://' + multihost.client.hostname + ':6636',
                                 'Credentials cache file.*not found|No Kerberos credentials available')

    @pytest.mark.tier1
    def test_0005_access_ldaps_with_simple_bind(self, multihost):
        """ IPA-TC: Functional Services: Access ldap with simple bind """
        multihost.master.qerun(['kdestroy', '-A'])
        ldap_simple_bind_check_positve(multihost.master,
                                       'ldaps://' + multihost.client.hostname + ':6636',
                                       'cn=Directory Manager', 'Secret123')

    @pytest.mark.tier1
    def test_0006_revoke_ldap_certificate(self, multihost):
        """ IPA-TC: Functional Services: Revoke ldap certificate """
        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa', 'service-show', '--all', '--raw',
                                            'ldap/' + multihost.client.hostname])
        serial_number = re.search('serial_number: (.+?)\n', cmd.stdout_text).group(1)
        multihost.master.qerun(['ipa', 'cert-revoke', serial_number])
        check_revoked(multihost.client, '/etc/dirsrv/slapd-instance1')

    @pytest.mark.tier2
    def test_0007_verify_cert_revoked_with_master_down(self, multihost):
        """ IPA-TC: Functional Services: Verify certificate is revoked when master is down """
        if not is_redundant_ca_dns_supported(multihost.client, 'ldap/' + multihost.client.hostname):
            pytest.skip('test requires Redundant ipa-ca dns name')
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipactl', 'stop'])
        errstr = ""
        try:
            check_revoked(multihost.client, '/etc/dirsrv/slapd-instance1')
        except ValueError as errval:
            errstr = str(errval.args[0])
        multihost.master.qerun(['ipactl', 'start'])
        check_revoked(multihost.client, '/etc/dirsrv/slapd-instance1')
        if errstr is not "":
            raise ValueError(errstr)

    @pytest.mark.tier2
    def test_0008_verify_cert_revoked_with_replica_down(self, multihost):
        """ IPA-TC: Functional Services: Verify certificate is revoked when replica is down """
        if not is_redundant_ca_dns_supported(multihost.client, 'ldap/' + multihost.client.hostname):
            pytest.skip('test requires Redundant ipa-ca dns name')
        multihost.replica.kinit_as_admin()
        multihost.replica.qerun(['ipactl', 'stop'])
        errstr = ""
        try:
            check_revoked(multihost.client, '/etc/dirsrv/slapd-instance1')
        except ValueError as errval:
            errstr = str(errval.args[0])
        multihost.replica.qerun(['ipactl', 'start'])
        check_revoked(multihost.client, '/etc/dirsrv/slapd-instance1')
        if errstr is not "":
            raise ValueError(errstr)

    @pytest.mark.tier2
    def test_0009_verify_ocsp_uri(self, multihost):
        """ IPA-TC: Functional Services: Verify OCSP URI has redundant DNS name """
        if not is_redundant_ca_dns_supported(multihost.client, 'ldap/' + multihost.client.hostname):
            pytest.skip('test requires Redundant ipa-ca dns name')
        multihost.client.kinit_as_admin()
        cmd = multihost.client.run_command(['ipa', 'service-show', '--all', '--raw',
                                            'ldap/' + multihost.client.hostname])
        serial_number = re.search('serial_number: (.+?)\n', cmd.stdout_text).group(1)
        url = 'http://ipa-ca.' + multihost.master.domain.name + ':80/ca/ocsp'
        cmd = multihost.client.run_command(['openssl', 'ocsp', '-issuer', '/etc/ipa/ca.crt',
                                            '-nonce', '-CAfile', '/etc/pki/tls/certs/ca-bundle.crt',
                                            '-url', url, '-serial', serial_number])

    def class_teardown(self, multihost):
        """ IPA-TC: Functional Services: Teardown LDAP Service software and requirements from test """
        pass
