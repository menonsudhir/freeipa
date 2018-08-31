""" Functional Services Setup for HTTP """
import re
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.shared.qe_certutils import certutil
import time


def setup_http_service(multihost):
    """ FS HTTP Service Setup """
    _http_install_software(multihost)
    _http_add_user(multihost)
    _http_add_service(multihost)
    _http_get_keytab(multihost)
    _http_setup_config(multihost)
    #_http_add_ipa_ca_cert(multihost)
    _http_cfg_ssl_with_cert(multihost)


def _http_install_software(multihost):
    """ class setup """
    multihost.client.qerun(['yum', '-y', '--nogpgcheck', 'install', 'httpd', 'mod_ssl',
                            'mod_auth_gssapi'])


def _http_add_user(multihost):
    """ Add an IPA User for http """
    add_ipa_user(multihost.master, "httpuser1")


def _http_add_service(multihost):
    """ Add an IPA service for http """
    multihost.master.kinit_as_admin()
    multihost.master.qerun(['ipa', 'service-add', 'HTTP/' + multihost.client.hostname])


def _http_get_keytab(multihost):
    """ get keytab for http """
    multihost.client.kinit_as_admin()
    multihost.client.qerun(['ipa-getkeytab', '-s', multihost.master.hostname,
                            '-k', '/etc/httpd/conf/func-services.keytab',
                            '-p', 'HTTP/' + multihost.client.hostname])
    multihost.client.qerun(['chown', 'apache.apache',
                            '/etc/httpd/conf/func-services.keytab'])


def _http_setup_config(multihost):
    """ configure http server """
    cfgget = '/opt/ipa_pytests/functional_services/http-gssapi.conf'
    cfgput = '/etc/httpd/conf.d/http-gssapi.conf'
    multihost.client.qerun(['rm', '-rf', cfgput])
    #multihost.client.put_file_contents(cfgput, cfgget)
    multihost.client.qerun(['cp', cfgget, cfgput])
    multihost.client.qerun(['service', 'httpd', 'start'])


def _http_add_ipa_ca_cert(multihost):
    """ Add IPA CA certificate to http server """
    crtget = "/etc/ipa/ca.crt"
    crtput = "/etc/httpd/alias/ca.crt"
    http_cert_db = "/etc/httpd/alias"
    nick = "IPA CA"
    trust = "CT,,"
    crtdata = multihost.master.get_file_contents(crtget)
    multihost.client.put_file_contents(crtput, crtdata)
    mycerts = certutil(multihost.client, http_cert_db)
    mycerts.add_cert(crtput, nick, trust)
    print(mycerts.list_certs()[0])


def _http_cfg_ssl_with_cert(multihost):
    """ Create Certficate for http service """
    multihost.client.qerun(['ipa-getcert', 'request',
                            '-k', '/etc/pki/tls/private/server.key',
                            '-f', '/etc/pki/tls/certs/server.crt'])
    time.sleep(30)
    nss_cfg_file = "/etc/httpd/conf.d/ssl.conf"
    nsscfg = multihost.client.get_file_contents(nss_cfg_file)

    CertFile = "SSLCertificateFile /etc/pki/tls/certs/localhost.crt"
    CertNewFile = "SSLCertificateFile /etc/pki/tls/certs/server.crt"
    nsscfg = re.sub(CertFile, CertNewFile, nsscfg)

    KeyFile = "SSLCertificateKeyFile /etc/pki/tls/private/localhost.key"
    KeyNewFile = "SSLCertificateKeyFile /etc/pki/tls/private/server.key"
    nsscfg = re.sub(KeyFile, KeyNewFile, nsscfg)

    CAFile = "#SSLCACertificateFile /etc/pki/tls/certs/ca-bundle.crt"
    CANewFile = "SSLCACertificateFile /etc/ipa/ca.crt"
    nsscfg = re.sub(CAFile, CANewFile, nsscfg)
    multihost.client.put_file_contents(nss_cfg_file, nsscfg)
    multihost.client.qerun(['service', 'httpd', 'restart'])
