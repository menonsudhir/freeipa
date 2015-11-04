""" Functional Services Setup for HTTP """
import re
from ipa_pytests.shared.utils import add_ipa_user
from ipa_pytests.shared.qe_certutils import certutil


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
    multihost.client.qerun(['yum', '-y', '--nogpgcheck', 'install', 'httpd', 'mod_nss',
                            'mod_auth_kerb'])


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
    cfgget = '/opt/ipa_pytests/functional_services/http-krb.conf'
    cfgput = '/etc/httpd/conf.d/http-krb.conf'
    multihost.client.qerun(['rm', '-rf', cfgput])
    httpcfg = multihost.client.get_file_contents(cfgget)
    httpcfg = re.sub('MY_VAR_REALM', multihost.client.domain.realm, httpcfg)
    multihost.client.put_file_contents(cfgput, httpcfg)
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
    multihost.client.qerun(['ipa', 'cert-request',
                            '--principal=HTTP/' + multihost.client.hostname,
                            csr_file])
    multihost.client.qerun(['ipa', 'service-show',
                            'HTTP/' + multihost.client.hostname,
                            '--out=' + crt_file])
    mycerts.add_cert(crt_file, nick, trust)
    mycerts.verify_cert(nick)

    nss_cfg_file = "/etc/httpd/conf.d/nss.conf"
    nsscfg = multihost.client.get_file_contents(nss_cfg_file)
    nsscfg = re.sub('Server-Cert', multihost.client.hostname, nsscfg)
    multihost.client.put_file_contents(nss_cfg_file, nsscfg)
    multihost.client.qerun(['service', 'httpd', 'restart'])
