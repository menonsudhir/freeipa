"""
Functional Services HTTP access tests
"""

import pytest
from ipa_pytests.functional_services import setup_lib_http


class TestHttpTests(object):
    """ FS HTTP Test access class """
    def class_setup(self, multihost):
        """ IPA-TC: Functional Services: Setup HTTP Service software and requirements for test """
        fin = '/tmp/ipa_func_svcs_setup_http_service_done'
        if not multihost.client.transport.file_exists(fin):
            setup_lib_http.setup_http_service(multihost)
            multihost.client.put_file_contents(fin, 'x')
        else:
            print "setup_http_service has already run...skipping"

    @pytest.mark.tier1
    def test_0001_access_http_with_valid_creds(self, multihost):
        """ IPA-TC: Functional Services: Access http server with valid credentials """
        url = "http://" + multihost.client.hostname + "/ipatest/"
        multihost.client.kinit_as_user('httpuser1', 'Secret123')
        multihost.client.qerun(['curl', '-v', '--negotiate', '-u:', url], exp_output='404')

    @pytest.mark.tier1
    def test_0002_access_http_without_valid_creds(self, multihost):
        """ IPA-TC: Functional Services: Access http server without valid credentials """
        url = "http://" + multihost.client.hostname + "/ipatest/"
        multihost.client.qerun(['kdestroy', '-A'])
        multihost.client.qerun(['curl', '-v', '--negotiate', '-u:', url], exp_output='401')

    @pytest.mark.tier2
    def test_0003_access_https_with_valid_creds(self, multihost):
        """ IPA-TC: Functional Services: Access https server with valid credentials """
        ipa_cert = "/etc/ipa/ca.crt"
        url = "https://" + multihost.client.hostname + ":443/ipatest/"
        multihost.client.kinit_as_user('httpuser1', 'Secret123')
        multihost.client.qerun(['curl', '-v', '--negotiate', '--cacert', ipa_cert, '-u:', url],
                               exp_output='404')

    @pytest.mark.tier2
    def test_0004_access_https_without_valid_creds(self, multihost):
        """ IPA-TC: Functional Services: Access https server without valid credentials """
        ipa_cert = "/etc/ipa/ca.crt"
        url = "https://" + multihost.client.hostname + ":443/ipatest/"
        multihost.client.qerun(['kdestroy', '-A'])
        multihost.client.qerun(['curl', '-v', '--negotiate', '--cacert', ipa_cert, '-u:', url],
                               exp_output='401')

    def class_teardown(self, multihost):
        """ IPA-TC: Functional Services: Teardown HTTP Service software and requirements from test """
        pass
