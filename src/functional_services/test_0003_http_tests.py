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
    def class_setup(self, multihost):
        """ class setup """
        print "\nClass Setup"
        print "MASTER: ", multihost.master.hostname
        print "REPLICA: ", multihost.replica.hostname
        print "CLIENT: ", multihost.client.hostname
        print "DNSFORWARD: ", multihost.config.dns_forwarder

    @pytest.mark.tier1
    def test_0001_access_http_with_valid_creds(self, multihost):
        """ Access http server with valid credentials """
        url = "http://" + multihost.client.hostname + "/ipatest/"
        multihost.client.kinit_as_user('httpuser1', 'Secret123')
        cmd = multihost.client.run_command(['curl', '-v', '--negotiate', '-u:', url])
        cmd.stdout_text.find('404')

    @pytest.mark.tier1
    def test_0002_access_http_without_valid_creds(self, multihost):
        """ Access http server without valid credentials """
        url = "http://" + multihost.client.hostname + "/ipatest/"
        multihost.client.run_command(['kdestroy', '-A'])
        cmd = multihost.client.run_command(['curl', '-v', '--negotiate', '-u:', url])
        cmd.stdout_text.find('401')

    @pytest.mark.tier2
    def test_0003_access_https_with_valid_creds(self, multihost):
        """ Access https server with valid credentials """
        ipa_cert = "/etc/ipa/ca.crt"
        url = "http://" + multihost.client.hostname + "/ipatest/"
        multihost.client.kinit_as_user('httpuser1', 'Secret123')
        cmd = multihost.client.run_command(['curl', '-v', '--negotiate', '--cacert',
                                            ipa_cert, '-u:', url])
        cmd.stdout_text.find('404')

    @pytest.mark.tier2
    def test_0004_access_http_without_valid_creds(self, multihost):
        """ Access https server without valid credentials """
        ipa_cert = "/etc/ipa/ca.crt"
        url = "http://" + multihost.client.hostname + "/ipatest/"
        multihost.client.run_command(['kdestroy', '-A'])
        cmd = multihost.client.run_command(['curl', '-v', '--negotiate', '--cacert',
                                            ipa_cert, '-u:', url])
        cmd.stdout_text.find('404')

    def class_teardown(self, multihost):
        """ class teardown """
        print "CLASS_TEARDOWN"
        print "MASTER: ", multihost.master.hostname
        print "REPLICA: ", multihost.replica.hostname
        print "CLIENT: ", multihost.client.hostname
        print "DNSFORWARD: ", multihost.config.dns_forwarder
