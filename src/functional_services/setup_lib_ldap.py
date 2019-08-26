""" Functional Services Setup for LDAP """
import re
import time
from .support import wait_for_ldap
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.shared.utils import ldapmodify_cmd
from ipa_pytests.shared.utils import service_control
from ipa_pytests.shared.qe_certutils import certutil


def setup_ldap_service(multihost):
    """ FS Setup LDAP Service """
    _ldap_install_software(multihost)
    _ldap_add_user(multihost)
    _ldap_add_service(multihost)
    _ldap_get_keytab(multihost)
    _ldap_initialize_instance(multihost)
    _ldap_set_password_scheme(multihost)
    _ldap_set_sasl(multihost)
    _ldap_set_cfg_krb_keytab(multihost)
    _ldap_add_user_to_directory(multihost)
    _ldap_add_ipa_ca_cert(multihost)
    _ldap_get_cert_for_service(multihost)
    _ldap_cfg_ssl_with_cert(multihost)


def _ldap_install_software(multihost):
    """ Install LDAP Software """
    multihost.client.qerun(['dnf', '-y', 'module', 'enable', '389-ds'])
    multihost.client.qerun(['dnf', '-y', 'install', 'net-tools', '389-ds-base', '389-ds-base-legacy-tools'])


def _ldap_add_user(multihost):
    """ Add IPA user for ldap """
    add_ipa_user(multihost.master, "ldapuser1")


def _ldap_add_service(multihost):
    """ Add IPA service for ldap """
    multihost.master.kinit_as_admin()
    multihost.master.qerun(['ipa', 'service-add', 'ldap/' + multihost.client.hostname])


def _ldap_get_keytab(multihost):
    """ Get keytab for ldap """
    multihost.client.kinit_as_admin()
    multihost.client.qerun(['ipa-getkeytab', '-s', multihost.master.hostname,
                            '-k', '/etc/dirsrv/ldap_service.keytab',
                            '-p', 'ldap/' + multihost.client.hostname])
    multihost.client.qerun(['chown', 'nobody.nobody', '/etc/dirsrv/ldap_service.keytab'])
    multihost.client.qerun(['chmod', '0400', '/etc/dirsrv/ldap_service.keytab'])


def _ldap_initialize_instance(multihost):
    """ Initialize ldap server instance """
    cfgget = '/opt/ipa_pytests/functional_services/ldap-instance.inf'
    cfgput = '/tmp/ldap-instance.inf'
    multihost.client.qerun(['rm', '-rf', cfgput])
    ldapcfg = multihost.client.get_file_contents(cfgget)
    ldapcfg = re.sub('MY_VAR_CLIENT', multihost.client.hostname, ldapcfg)
    ldapcfg = re.sub('MY_VAR_PORT', '3389', ldapcfg)
    multihost.client.put_file_contents(cfgput, ldapcfg)
    multihost.client.qerun(['semanage', 'port', '--add', '-t', 'ldap_port_t', '-p', 'tcp', '3389'])
    multihost.client.qerun(['/usr/sbin/setup-ds.pl', '--silent', '--file=' + cfgput])
    time.sleep(60)


def _ldap_set_password_scheme(multihost):
    """ Configure ldap password scheme """
    uri = 'ldap://' + multihost.client.hostname + ':3389'
    username = 'cn=Directory Manager'
    password = 'Secret123'
    ldif_file = '/opt/ipa_pytests/functional_services/ldap-pwscheme.ldif'
    ldapmodify_cmd(multihost.master, uri, username, password, ldif_file)


def _ldap_set_sasl(multihost):
    """ Configure ldap sasl """
    uri = 'ldap://' + multihost.client.hostname + ':3389'
    username = 'cn=Directory Manager'
    password = 'Secret123'
    ldif_file = '/opt/ipa_pytests/functional_services/ldap-sasl.ldif'
    ldapmodify_cmd(multihost.master, uri, username, password, ldif_file)


def _ldap_set_cfg_krb_keytab(multihost):
    """ Configure ldap to point to keytab """
    cfg = '/etc/sysconfig/dirsrv-instance1'
    ldapcfg = multihost.client.get_file_contents(cfg)
    ldapcfg = ldapcfg + '\nKRB5_KTNAME=/etc/dirsrv/ldap_service.keytab\n'
    multihost.client.put_file_contents(cfg, ldapcfg)
    multihost.client.qerun(['systemctl', 'daemon-reload'])
    service_control(multihost.client, 'dirsrv@instance1', 'restart')
    wait_for_ldap(multihost.client, '3389')
    time.sleep(30)


def _ldap_add_user_to_directory(multihost):
    """ Add ldap user in ldap """
    uri = 'ldap://' + multihost.client.hostname + ':3389'
    username = 'cn=Directory Manager'
    password = 'Secret123'
    ldif_file = '/opt/ipa_pytests/functional_services/ldap-user.ldif'
    ldapmodify_cmd(multihost.master, uri, username, password, ldif_file)


def _ldap_add_ipa_ca_cert(multihost):
    """ Add IPA CA certificate to ldap """
    crtget = "/etc/ipa/ca.crt"
    crtput = "/etc/dirsrv/slapd-instance1/ca.crt"
    ldap_cert_db = "/etc/dirsrv/slapd-instance1"
    nick = "IPA CA"
    trust = "CT,,"
    crtdata = multihost.master.get_file_contents(crtget)
    multihost.client.put_file_contents(crtput, crtdata)
    mycerts = certutil(multihost.client, ldap_cert_db)
    mycerts.add_cert(crtput, nick, trust)


def _ldap_get_cert_for_service(multihost):
    """ Create certificate for ldap service """
    ldap_cert_db = "/etc/dirsrv/slapd-instance1"
    nick = multihost.client.hostname
    trust = "u,u,u"
    csr_file = "/tmp/ldap-func-services.csr"
    crt_file = "/tmp/ldap-func-services.crt"
    mycerts = certutil(multihost.client, ldap_cert_db)
    subject_base = mycerts.get_ipa_subject_base(multihost.master)
    subject = "CN=" + multihost.client.hostname + "," + subject_base
    mycerts.request_cert(subject, csr_file)
    multihost.client.qerun(['ipa', 'cert-request',
                            '--principal=ldap/' + multihost.client.hostname,
                            csr_file])
    multihost.client.qerun(['ipa', 'service-show',
                            'ldap/' + multihost.client.hostname,
                            '--out=' + crt_file])
    mycerts.add_cert(crt_file, nick, trust)
    mycerts.verify_cert(nick)


def _ldap_cfg_ssl_with_cert(multihost):
    """ Configure ldap to enable ssl """
    uri = 'ldap://' + multihost.client.hostname + ':3389'
    username = 'cn=Directory Manager'
    password = 'Secret123'
    ldif_get = '/opt/ipa_pytests/functional_services/ldap-enablessl.ldif'
    ldif_put = '/tmp/mytest-ldap-enablessl.ldif'
    ldapcfg = multihost.master.get_file_contents(ldif_get)
    ldapcfg = re.sub('MY_VAR_CLIENT', multihost.client.hostname, ldapcfg)
    ldapcfg = re.sub('MY_VAR_SECURE_PORT', '6636', ldapcfg)
    # must put to master here because that's where ldapmodify is run from
    multihost.master.put_file_contents(ldif_put, ldapcfg)
    ldapmodify_cmd(multihost.master, uri, username, password, ldif_put)
    #pin = "Internal (Software) Token:Secret123"
    #pin_file = "/etc/dirsrv/slapd-instance1/pin.txt"
    #multihost.client.put_file_contents(pin_file, pin)
    multihost.client.qerun(['semanage', 'port', '-a', '-t', 'ldap_port_t',
                            '-p', 'tcp', '6636'])
    service_control(multihost.client, 'dirsrv@instance1', 'restart')
    wait_for_ldap(multihost.client, '3389')
    time.sleep(60)
