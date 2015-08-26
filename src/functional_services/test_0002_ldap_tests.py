"""
Functional Services LDAP Access Tests
"""

import pytest
import re
import socket
from .setup_lib_ldap import setup_ldap_service
from .support import ldap_sasl_check_positive
from .support import ldap_sasl_check_negative
from .support import ldap_simple_bind_check_positve
from .support import is_redundant_ca_dns_supported
from .support import check_revoked


class TestLdap(object):
    """ FS LDAP Tests class """
    def class_setup(self, multihost):
        """ Setup LDAP Service software and requirements for test """
        fin = '/tmp/ipa_func_svcs_setup_ldap_service_done'
        if not multihost.client.transport.file_exists(fin):
            setup_ldap_service(multihost)
            multihost.client.put_file_contents(fin, 'x')
        else:
            print "setup_ldap_service has already run...skipping"

    @pytest.mark.tier1
    def ipa_func_svcs_0001_access_ldap_with_creds(self, multihost):
        """ Access ldap with valid credentials """
        myself = multihost.config.host_by_name(socket.gethostname())
        myself.kinit_as_user('ldapuser1', 'Secret123')
        ldap_sasl_check_positive('ldap://' + multihost.client.hostname + ':3389')

    @pytest.mark.tier1
    def ipa_func_svcs_0002_deny_ldap_without_creds(self, multihost):
        """ deny access to ldap without valid credentials """
        myself = multihost.config.host_by_name(socket.gethostname())
        myself.qerun(['kdestroy', '-A'])
        ldap_sasl_check_negative('ldap://' + multihost.client.hostname + ':3389',
                                 'Credentials cache file.*not found|No Kerberos credentials available')

    @pytest.mark.tier1
    def ipa_func_svcs_0003_access_ldaps_with_creds(self, multihost):
        """ Access ldaps with valid credentials """
        myself = multihost.config.host_by_name(socket.gethostname())
        myself.kinit_as_user('ldapuser1', 'Secret123')
        ldap_sasl_check_positive('ldaps://' + multihost.client.hostname + ':6636')

    @pytest.mark.tier1
    def ipa_func_svcs_0004_deny_ldaps_without_creds(self, multihost):
        """ deny access to ldaps without valid credentials """
        myself = multihost.config.host_by_name(socket.gethostname())
        myself.qerun(['kdestroy', '-A'])
        ldap_sasl_check_negative('ldaps://' + multihost.client.hostname + ':6636',
                                 'Credentials cache file.*not found|No Kerberos credentials available')

    @pytest.mark.tier1
    def ipa_func_svcs_0005_access_ldaps_with_simple_bind(self, multihost):
        """ Access ldap with simple bind """
        myself = multihost.config.host_by_name(socket.gethostname())
        myself.qerun(['kdestroy', '-A'])
        ldap_simple_bind_check_positve('ldaps://' + multihost.client.hostname + ':6636',
                                       'cn=Directory Manager', 'Secret123')

    @pytest.mark.tier1
    def ipa_func_svcs_0006_revoke_ldap_certificate(self, multihost):
        """ Revoke ldap certificate """
        myself = multihost.config.host_by_name(socket.gethostname())
        myself.kinit_as_admin()
        cmd = myself.run_command(['ipa', 'service-show', '--all', '--raw',
                                  'ldap/' + multihost.client.hostname])
        serial_number = re.search('serial_number: (.+?)\n', cmd.stdout_text).group(1)
        myself.qerun(['ipa', 'cert-revoke', serial_number])
        check_revoked(multihost.client, '/etc/dirsrv/slapd-instance1')

    @pytest.mark.tier2
    def ipa_func_svcs_0007_verify_cert_revoked_with_master_down(self, multihost):
        """ Verify certificate is revoked when master is down """
        if not is_redundant_ca_dns_supported(multihost.client, 'ldap/' + multihost.client.hostname):
            pytest.skip('test requires Redundant ipa-ca dns name')
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipactl', 'stop'])
        errstr = ""
        try:
            check_revoked(multihost.client, '/etc/dirsrv/slapd-instance1')
        except ValueError, errval:
            errstr = str(errval.args[0])
        multihost.master.qerun(['ipactl', 'start'])
        check_revoked(multihost.client, '/etc/dirsrv/slapd-instance1')
        if errstr is not "":
            raise ValueError(errstr)

    @pytest.mark.tier2
    def ipa_func_svcs_0008_verify_cert_revoked_with_replica_down(self, multihost):
        """ Verify certificate is revoked when replica is down """
        if not is_redundant_ca_dns_supported(multihost.client, 'ldap/' + multihost.client.hostname):
            pytest.skip('test requires Redundant ipa-ca dns name')
        multihost.replica.kinit_as_admin()
        multihost.replica.qerun(['ipactl', 'stop'])
        errstr = ""
        try:
            check_revoked(multihost.client, '/etc/dirsrv/slapd-instance1')
        except ValueError, errval:
            errstr = str(errval.args[0])
        multihost.replica.qerun(['ipactl', 'start'])
        check_revoked(multihost.client, '/etc/dirsrv/slapd-instance1')
        if errstr is not "":
            raise ValueError(errstr)

    @pytest.mark.tier2
    def ipa_func_svcs_0009_verify_ocsp_uri(self, multihost):
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

    def class_teardown(self, multihost):
        """ Teardown LDAP Service software and requirements from test """
        pass
