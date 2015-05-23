"""
Functional Services LDAP Access Tests
"""

import pytest
import ldap
import ldap.sasl
import re
import socket


def ldap_sasl_check_positive(uri):
    """ support function to check ldap access for success """
    ldapobj = ldap.initialize(uri)
    ldapobj.set_option(ldap.OPT_X_TLS_DEMAND, True)
    auth = ldap.sasl.gssapi('')
    try:
        ldapobj.sasl_interactive_bind_s('ldapuser1', auth)
    except Exception:
        raise ValueError('[Fail]: sasl bind failed')


def ldap_sasl_check_negative(uri, expected_message):
    """ support function to check ldap access for denial """
    ldapobj = ldap.initialize(uri)
    ldapobj.set_option(ldap.OPT_X_TLS_DEMAND, True)
    auth = ldap.sasl.gssapi('')
    try:
        ldapobj.sasl_interactive_bind_s('ldapuser1', auth)
    except ldap.LOCAL_ERROR, errval:
        if not re.search(expected_message, errval.args[0]['info']):
            print "ERROR: ", errval.args[0]['info']
            raise ValueError('[Fail]: sasl bind did not fail as expected')
    else:
        raise ValueError('[Fail]: sasl bind passed when it should fail')


def ldap_simple_bind_check_positve(uri, username, password):
    """ support function to check simple ldap bind """
    ldapobj = ldap.initialize(uri)
    try:
        ldapobj.simple_bind_s(username, password)
    except Exception:
        raise ValueError('[Fail]: unable to bind with user and password')


def check_revoked(host, cert_dir):
    """ support function to check if certificate is revoked """
    max_checks = 5
    if host.transport.file_exists('/usr/lib64/nss/unsupported-tools/ocspclnt'):
        ocspcmd = '/usr/lib64/nss/unsupported-tools/ocspclnt'
    else:
        ocspcmd = '/usr/lib/nss/unsupported-tools/ocspclnt'

    for _ in range(max_checks):
        cmd = host.run_command([ocspcmd, '-S', host.hostname, '-d', cert_dir])
        if 'Certificate has been revoked' in cmd.stdout_text:
            print "stdout: %s" % cmd.stdout_text
            return
        else:
            print "There was an error.   Checking again to be sure"
            print "stdout: %s" % cmd.stdout_text
            print "stderr: %s" % cmd.stderr_text

    raise ValueError('Certificate not revoked or unable to check')


def is_redundant_ca_dns_supported(host, service):
    """ support function to test if ipa-ca DNS name supported """
    host.kinit_as_admin()
    cmd = host.run_command(['ipa', 'service-show', '--all', '--raw', service])
    serial_number = re.search('serial_number: (.+?)\n', cmd.stdout_text).group(1)
    host.run_command(['ipa', 'cert-show', serial_number, '--out=/tmp/cert_to_check.crt'])
    cmd = host.run_command(['openssl', 'x509', '-text', '-in', '/tmp/cert_to_check.crt'])
    if re.search('OCSP.*URI.*http://ipa-ca', cmd.stdout_text):
        print "ipa-ca redundant dns URI found"
        return True
    else:
        print "ipa-ca redundant dns URI not found"
        return False


class TestLdap(object):
    """ FS LDAP Tests class """
    @pytest.mark.tier1
    def test_0001_access_ldap_with_creds(self, multihost):
        """ Access ldap with valid credentials """
        myself = multihost.config.host_by_name(socket.gethostname())
        myself.kinit_as_user('ldapuser1', 'Secret123')
        ldap_sasl_check_positive('ldap://' + multihost.client.hostname + ':3389')

    @pytest.mark.tier1
    def test_0002_deny_ldap_without_creds(self, multihost):
        """ deny access to ldap without valid credentials """
        myself = multihost.config.host_by_name(socket.gethostname())
        myself.run_command(['kdestroy', '-A'])
        ldap_sasl_check_negative('ldap://' + multihost.client.hostname + ':3389',
                                 'Credentials cache file.*not found|No Kerberos credentials available')

    @pytest.mark.tier1
    def test_0003_access_ldaps_with_creds(self, multihost):
        """ Access ldaps with valid credentials """
        myself = multihost.config.host_by_name(socket.gethostname())
        myself.kinit_as_user('ldapuser1', 'Secret123')
        ldap_sasl_check_positive('ldaps://' + multihost.client.hostname + ':6636')

    @pytest.mark.tier1
    def test_0004_deny_ldaps_without_creds(self, multihost):
        """ deny access to ldaps without valid credentials """
        myself = multihost.config.host_by_name(socket.gethostname())
        myself.run_command(['kdestroy', '-A'])
        ldap_sasl_check_negative('ldaps://' + multihost.client.hostname + ':6636',
                                 'Credentials cache file.*not found|No Kerberos credentials available')

    @pytest.mark.tier1
    def test_0005_access_ldaps_with_simple_bind(self, multihost):
        """ Access ldap with simple bind """
        myself = multihost.config.host_by_name(socket.gethostname())
        myself.run_command(['kdestroy', '-A'])
        ldap_simple_bind_check_positve('ldaps://' + multihost.client.hostname + ':6636',
                                       'cn=Directory Manager', 'Secret123')

    @pytest.mark.tier1
    def test_0006_revoke_ldap_certificate(self, multihost):
        """ Revoke ldap certificate """
        myself = multihost.config.host_by_name(socket.gethostname())
        myself.kinit_as_admin()
        cmd = myself.run_command(['ipa', 'service-show', '--all', '--raw',
                                  'ldap/' + multihost.client.hostname])
        serial_number = re.search('serial_number: (.+?)\n', cmd.stdout_text).group(1)
        myself.run_command(['ipa', 'cert-revoke', serial_number])
        check_revoked(multihost.client, '/etc/dirsrv/slapd-instance1')

    @pytest.mark.tier2
    def test_0007_verify_cert_revoked_with_master_down(self, multihost):
        """ Verify certificate is revoked when master is down """
        if not is_redundant_ca_dns_supported(multihost.client, 'ldap/' + multihost.client.hostname):
            pytest.skip('test requires Redundant ipa-ca dns name')
        multihost.master.kinit_as_admin()
        multihost.master.run_command(['ipactl', 'stop'])
        check_revoked(multihost.client, '/etc/dirsrv/slapd-instance1')
        multihost.master.run_command(['ipactl', 'start'])
        check_revoked(multihost.client, '/etc/dirsrv/slapd-instance1')

    @pytest.mark.tier2
    def test_0008_verify_cert_revoked_with_replica_down(self, multihost):
        """ Verify certificate is revoked when replica is down """
        if not is_redundant_ca_dns_supported(multihost.client, 'ldap/' + multihost.client.hostname):
            pytest.skip('test requires Redundant ipa-ca dns name')
        multihost.replica.kinit_as_admin()
        multihost.replica.run_command(['ipactl', 'stop'])
        check_revoked(multihost.client, '/etc/dirsrv/slapd-instance1')
        multihost.replica.run_command(['ipactl', 'start'])
        check_revoked(multihost.client, '/etc/dirsrv/slapd-instance1')

    @pytest.mark.tier2
    def test_0009_verify_ocsp_uri(self, multihost):
        """ Verify OCSP URI has redundant DNS name """
        if not is_redundant_ca_dns_supported(multihost.client, 'ldap/' + multihost.client.hostname):
            pytest.skip('test requires Redundant ipa-ca dns name')
        multihost.client.kinit_as_admin()
        cmd = multihost.client.run_command(['ipa', 'service-show', '--all', '--raw',
                                            'ldap/' + multihost.client.hostname])
        serial_number = re.search('serial_number: (.+?)\n', cmd.stdout_text).group(1)
        url = 'http://ipa-ca.' + multihost.domain.name + ':80/ca/ocsp'
        cmd = multihost.client.run_command(['openssl', 'ocsp', '-issuer', '/etc/ipa/ca.crt',
                                            '-nonce', '-CAfile', '/etc/pki/tls/certs/ca-bundle.crt',
                                            '-url', url, '-serial', serial_number])
