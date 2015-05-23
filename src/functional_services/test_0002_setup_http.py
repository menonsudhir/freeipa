"""
Functional Services HTTP Configuration including certificate and service setup.
"""

import re
import pytest
import requests
from ipa_pytests.shared.utils import add_ipa_user
from ipa_pytests.shared.qe_certutils import certutil


class TestSetupHttp(object):
    """ FS HTTP setup Class """
    def class_setup(self, multihost):
        """ class setup """
        multihost.client.run_command(['yum', '-y', '--nogpgcheck', 'install', 'httpd', 'mod_nss', 'mod_auth_kerb'])
        revip = multihost.client.ip.split('.')[3]
        revnet = multihost.client.ip.split('.')[2] + '.' + \
            multihost.client.ip.split('.')[1] + '.' + \
            multihost.client.ip.split('.')[0] + '.in-addr.arpa.'
        cmd = multihost.client.run_command(['dig', '+short', '-x', multihost.client.ip])
        if multihost.client.hostname not in cmd.stdout_text:
            multihost.master.kinit_as_admin()
            cmd = multihost.master.run_command(['ipa', 'dnsrecord-add', revnet, revip,
                                                '--ptr-rec=%s.' % multihost.client.hostname])

    @pytest.mark.tier1
    def test_0001_add_http_user(self, multihost):
        """ Add an IPA User for http """
        add_ipa_user(multihost.master, "httpuser1")

    @pytest.mark.tier1
    def test_0002_add_http_service(self, multihost):
        """ Add an IPA service for http """
        multihost.master.kinit_as_admin()
        multihost.master.run_command(['ipa', 'service-add', 'HTTP/' + multihost.client.hostname])

    @pytest.mark.tier1
    def test_0003_get_http_keytab(self, multihost):
        """ get keytab for http """
        multihost.client.kinit_as_admin()
        multihost.client.run_command(['ipa-getkeytab', '-s', multihost.master.hostname,
                                      '-k', '/etc/httpd/conf/func-services.keytab',
                                      '-p', 'HTTP/' + multihost.client.hostname])
        multihost.client.run_command(['chown', 'apache.apache',
                                      '/etc/httpd/conf/func-services.keytab'])

    @pytest.mark.tier1
    def test_0004_setup_http_config(self, multihost):
        """ configure http server """
        cfgget = '/opt/ipa_pytests/functional_services/http-krb.conf'
        cfgput = '/etc/httpd/conf.d/http-krb.conf'
        multihost.client.run_command(['rm', '-rf', cfgput])
        httpcfg = multihost.client.get_file_contents(cfgget)
        httpcfg = re.sub('MY_VAR_REALM', multihost.client.domain.realm, httpcfg)
        multihost.client.put_file_contents(cfgput, httpcfg)
        multihost.client.run_command(['service', 'httpd', 'start'])

    @pytest.mark.tier1
    def test_0005_add_ipa_ca_cert_to_http(self, multihost):
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

    @pytest.mark.tier1
    def test_0006_get_cert_for_http_service(self, multihost):
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

    def class_teardown(self, multihost):
        """ class teardown """
        pass
