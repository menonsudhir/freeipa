""" Functional Services Setup Support Functions
This includes functions to help setup:
- IPA Env
- HTTP Service
- LDAP Service
"""

import re
import requests
import socket
import time
from ipa_pytests.qe_install import setup_master, setup_replica, setup_client
from ipa_pytests.qe_install import set_resolv_conf_add_server
from ipa_pytests.shared.utils import add_ipa_user
from ipa_pytests.shared.utils import ldapmodify
from ipa_pytests.shared.qe_certutils import certutil


# IPA ###############################################################

def setup_ipa_env(multihost):
    """ Setup IPA Env with Master, Replica, Client """
    _ipa_master(multihost)
    _ipa_replica(multihost)
    _ipa_client(multihost)


def _ipa_master(multihost):
    """ Install IPA Master """
    setup_master(multihost.master)
    set_resolv_conf_add_server(multihost.master, multihost.replica.ip)


def _ipa_replica(multihost):
    """ Install IPA Replica """
    setup_replica(multihost.replica, multihost.master)
    set_resolv_conf_add_server(multihost.replica, multihost.master.ip)


def _ipa_client(multihost):
    """ Install IPA Client """
    setup_client(multihost.client, multihost.master)
    set_resolv_conf_add_server(multihost.client, multihost.replica.ip)
    revip = multihost.client.ip.split('.')[3]
    revnet = multihost.client.ip.split('.')[2] + '.' + \
        multihost.client.ip.split('.')[1] + '.' + \
        multihost.client.ip.split('.')[0] + '.in-addr.arpa.'
    cmd = multihost.client.run_command(['dig', '+short', '-x', multihost.client.ip])
    if multihost.client.hostname not in cmd.stdout_text:
        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa', 'dnsrecord-add', revnet, revip,
                                            '--ptr-rec=%s.' % multihost.client.hostname])

# HTTP ##############################################################


def setup_http_service(multihost):
    """ FS HTTP Service Setup """
    _http_install_software(multihost)
    _http_add_user(multihost)
    _http_add_service(multihost)
    _http_get_keytab(multihost)
    _http_setup_config(multihost)
    _http_add_ipa_ca_cert(multihost)
    _http_cfg_ssl_with_cert(multihost)


def _http_install_software(multihost):
    """ class setup """
    multihost.client.run_command(['yum', '-y', '--nogpgcheck', 'install', 'httpd', 'mod_nss', 'mod_auth_kerb'])


def _http_add_user(multihost):
    """ Add an IPA User for http """
    add_ipa_user(multihost.master, "httpuser1")


def _http_add_service(multihost):
    """ Add an IPA service for http """
    multihost.master.kinit_as_admin()
    multihost.master.run_command(['ipa', 'service-add', 'HTTP/' + multihost.client.hostname])


def _http_get_keytab(multihost):
    """ get keytab for http """
    multihost.client.kinit_as_admin()
    multihost.client.run_command(['ipa-getkeytab', '-s', multihost.master.hostname,
                                  '-k', '/etc/httpd/conf/func-services.keytab',
                                  '-p', 'HTTP/' + multihost.client.hostname])
    multihost.client.run_command(['chown', 'apache.apache',
                                  '/etc/httpd/conf/func-services.keytab'])


def _http_setup_config(multihost):
    """ configure http server """
    cfgget = '/opt/ipa_pytests/functional_services/http-krb.conf'
    cfgput = '/etc/httpd/conf.d/http-krb.conf'
    multihost.client.run_command(['rm', '-rf', cfgput])
    httpcfg = multihost.client.get_file_contents(cfgget)
    httpcfg = re.sub('MY_VAR_REALM', multihost.client.domain.realm, httpcfg)
    multihost.client.put_file_contents(cfgput, httpcfg)
    multihost.client.run_command(['service', 'httpd', 'start'])


def _http_add_ipa_ca_cert(multihost):
    """ Add IPA CA certificate to http server """
    crtget = "http://" + multihost.master.hostname + "/ipa/config/ca.crt"
    crtput = "/etc/httpd/alias/ca.crt"
    http_cert_db = "/etc/httpd/alias"
    nick = "IPA CA"
    trust = "CT,,"
    crtdata = requests.get(crtget).text
    multihost.client.put_file_contents(crtput, crtdata)
    mycerts = certutil(multihost.client, http_cert_db)
    mycerts.add_cert(crtput, nick, trust)
    print mycerts.list_certs()[0]


def _http_cfg_ssl_with_cert(multihost):
    """ Create Certficate for http service """
    http_cert_db = "/etc/httpd/alias"
    nick = multihost.client.hostname
    trust = "u,u,u"
    csr_file = "/tmp/http-func-services.csr"
    crt_file = "/tmp/http-func-services.crt"
    mycerts = certutil(multihost.client, http_cert_db)
    subject_base = mycerts.get_ipa_subject_base(multihost.master)
    subject = "CN=" + multihost.client.hostname + "," + subject_base
    mycerts.request_cert(subject, csr_file)
    multihost.client.run_command(['ipa', 'cert-request',
                                  '--principal=HTTP/' + multihost.client.hostname,
                                  csr_file])
    multihost.client.run_command(['ipa', 'service-show',
                                  'HTTP/' + multihost.client.hostname,
                                  '--out=' + crt_file])
    mycerts.add_cert(crt_file, nick, trust)
    mycerts.verify_cert(nick)

    nss_cfg_file = "/etc/httpd/conf.d/nss.conf"
    nsscfg = multihost.client.get_file_contents(nss_cfg_file)
    nsscfg = re.sub('Server-Cert', multihost.client.hostname, nsscfg)
    multihost.client.put_file_contents(nss_cfg_file, nsscfg)
    multihost.client.run_command(['service', 'httpd', 'restart'])

# LDAP ##############################################################


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
    multihost.client.run_command(['yum', '-y', '--nogpgcheck', 'install', '389-ds-base'])


def _ldap_add_user(multihost):
    """ Add IPA user for ldap """
    add_ipa_user(multihost.master, "ldapuser1")


def _ldap_add_service(multihost):
    """ Add IPA service for ldap """
    multihost.master.kinit_as_admin()
    multihost.master.run_command(['ipa', 'service-add', 'ldap/' + multihost.client.hostname])


def _ldap_get_keytab(multihost):
    """ Get keytab for ldap """
    multihost.client.kinit_as_admin()
    multihost.client.run_command(['ipa-getkeytab', '-s', multihost.master.hostname,
                                  '-k', '/etc/dirsrv/ldap_service.keytab',
                                  '-p', 'ldap/' + multihost.client.hostname])
    multihost.client.run_command(['chown', 'nobody.nobody',
                                  '/etc/dirsrv/ldap_service.keytab'])
    multihost.client.run_command(['chmod', '0400',
                                  '/etc/dirsrv/ldap_service.keytab'])


def _ldap_initialize_instance(multihost):
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
    time.sleep(5)


def _ldap_set_password_scheme(multihost):
    """ Configure ldap password scheme """
    uri = 'ldap://' + multihost.client.hostname + ':3389'
    username = 'cn=Directory Manager'
    password = 'Secret123'
    ldif_file = '/opt/ipa_pytests/functional_services/ldap-pwscheme.ldif'
    ldapmodify(uri, username, password, ldif_file)


def _ldap_set_sasl(multihost):
    """ Configure ldap sasl """
    uri = 'ldap://' + multihost.client.hostname + ':3389'
    username = 'cn=Directory Manager'
    password = 'Secret123'
    ldif_file = '/opt/ipa_pytests/functional_services/ldap-sasl.ldif'
    ldapmodify(uri, username, password, ldif_file)


def _ldap_set_cfg_krb_keytab(multihost):
    """ Configure ldap to point to keytab """
    cfgget = '/etc/sysconfig/dirsrv'
    cfgput = '/etc/sysconfig/dirsrv'
    ldapcfg = multihost.client.get_file_contents(cfgget)
    if multihost.client.transport.file_exists('/usr/lib/systemd/system/dirsrv@.service'):
        ldapcfg = ldapcfg + '\nKRB5_KTNAME=/etc/dirsrv/ldap_service.keytab\n'
    else:
        ldapcfg = ldapcfg + '\nKRB5_KTNAME=/etc/dirsrv/ldap_service.keytab ; export KRB5_KTNAME\n'
    multihost.client.put_file_contents(cfgput, ldapcfg)
    multihost.client.run_command(['service', 'dirsrv@instance1', 'restart'])
    time.sleep(5)


def _ldap_add_user_to_directory(multihost):
    """ Add ldap user in ldap """
    uri = 'ldap://' + multihost.client.hostname + ':3389'
    username = 'cn=Directory Manager'
    password = 'Secret123'
    ldif_file = '/opt/ipa_pytests/functional_services/ldap-user.ldif'
    ldapmodify(uri, username, password, ldif_file)


def _ldap_add_ipa_ca_cert(multihost):
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
    multihost.client.run_command(['ipa', 'cert-request',
                                  '--principal=ldap/' + multihost.client.hostname,
                                  csr_file])
    multihost.client.run_command(['ipa', 'service-show',
                                  'ldap/' + multihost.client.hostname,
                                  '--out=' + crt_file])
    mycerts.add_cert(crt_file, nick, trust)
    mycerts.verify_cert(nick)


def _ldap_cfg_ssl_with_cert(multihost):
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
    multihost.client.run_command(['service', 'dirsrv@instance1', 'restart'])
    time.sleep(5)
