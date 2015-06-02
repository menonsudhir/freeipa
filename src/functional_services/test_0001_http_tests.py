"""
Functional Services HTTP access tests
"""

import pytest


def curl_check(host, url):
    """ support function to check http access with curl command """
    cmd = host.run_command(['curl', '-v', '--negotiate', '-u:', url])
    return cmd.stdout_text


class TestHttpTests(object):
    """ FS HTTP Test access class """
    @pytest.mark.tier1
    def ipa_func_svcs_0001_access_http_with_valid_creds(self, multihost):
        """ Access http server with valid credentials """
        url = "http://" + multihost.client.hostname + "/ipatest/"
        multihost.client.kinit_as_user('httpuser1', 'Secret123')
        cmd = multihost.client.run_command(['curl', '-v', '--negotiate', '-u:', url])
        cmd.stdout_text.find('404')

    @pytest.mark.tier1
    def ipa_func_svcs_0002_access_http_without_valid_creds(self, multihost):
        """ Access http server without valid credentials """
        url = "http://" + multihost.client.hostname + "/ipatest/"
        multihost.client.run_command(['kdestroy', '-A'])
        cmd = multihost.client.run_command(['curl', '-v', '--negotiate', '-u:', url])
        cmd.stdout_text.find('401')

    @pytest.mark.tier2
    def ipa_func_svcs_0003_access_https_with_valid_creds(self, multihost):
        """ Access https server with valid credentials """
        ipa_cert = "/etc/ipa/ca.crt"
        url = "https://" + multihost.client.hostname + ":8443/ipatest/"
        multihost.client.kinit_as_user('httpuser1', 'Secret123')
        cmd = multihost.client.run_command(['curl', '-v', '--negotiate', '--cacert',
                                            ipa_cert, '-u:', url])
        cmd.stdout_text.find('404')

    @pytest.mark.tier2
    def ipa_func_svcs_0004_access_https_without_valid_creds(self, multihost):
        """ Access https server without valid credentials """
        ipa_cert = "/etc/ipa/ca.crt"
        url = "https://" + multihost.client.hostname + ":8443/ipatest/"
        multihost.client.run_command(['kdestroy', '-A'])
        cmd = multihost.client.run_command(['curl', '-v', '--negotiate', '--cacert',
                                            ipa_cert, '-u:', url])
        cmd.stdout_text.find('404')
