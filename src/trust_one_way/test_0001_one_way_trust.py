"""
This covers the test cases for one way trust feature
"""

from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.shared.utils import (disable_dnssec, dnsforwardzone_add,
                                      add_dnsforwarder)
from ipa_pytests.qe_install import adtrust_install
import pytest
import time


class TestOneWay(object):
    """
    This covers the test cases for RFE bugzilla 1145748
    """
    def class_setup(self, multihost):
        """ Setup for class """
        disable_dnssec(multihost.master)

        adtrust_install(multihost.master)

        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])
        domain = multihost.master.domain.name

        etchosts = '/etc/hosts'
        etchostscfg = multihost.master.get_file_contents(etchosts)
        etchostscfg += '\n' + ad1.ip + ' ' + ad1.hostname + '\n'
        multihost.master.put_file_contents(etchosts, etchostscfg)

        dnsforwardzone_add(multihost.master, forwardzone, ad1.ip)

        add_dnsforwarder(ad1, domain, multihost.master.ip)

        cmd = multihost.master.run_command('dig +short SRV _ldap._tcp.' + forwardzone,
                                           raiseonerr=False)
        print cmd.stdout_text
        if ad1.hostname in cmd.stdout_text:
            print("dns resolution passed for ad domain")
        else:
            pytest.xfail("dns resolution failed for ad domain")
        cmd = multihost.master.run_command('dig +short SRV @' + ad1.ip +
                                           ' _ldap._tcp.' + domain,
                                           raiseonerr=False)
        print cmd.stdout_text
        if domain in cmd.stdout_text:
            print("dns resolution passed for ipa domain")
        else:
            pytest.xfail("dns resolution failed for ipa domain")

    def test_001_one_way_trust_add(self, multihost):
        """
        This test case add one way trust and checks it works
        """
        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])
        cmd = multihost.master.run_command(['ipa', 'trust-add', forwardzone,
                                            '--admin', ad1.ssh_username,
                                            '--type=ad',
                                            '--range-type=ipa-ad-trust'],
                                           stdin_text=ad1.ssh_password,
                                           raiseonerr=False)
        print cmd.stdout_text
        if "Trust direction: Trusting forest" in cmd.stdout_text:
            print "One way trust establised successfully"
        else:
            pytest.xfail("One way trust addition failed")
        print cmd.stderr_text
        print "waiting for 60 seconds"
        time.sleep(60)
        cmd = multihost.master.run_command('ipactl restart', raiseonerr=False)
        print cmd.stdout_text
        print "waiting for 60 seconds"
        time.sleep(60)
        cmd = multihost.master.run_command('id aduser1@' + forwardzone, raiseonerr=False)
        print cmd.stdout_text
        print cmd.stderr_text
        if "aduser1" in cmd.stdout_text:
            print "AD user resolved on IPA"
        else:
            pytest.xfail("AD user not resolved on IPA ")
        print cmd.stderr_text

    def class_teardown(self, multihost):
        """ Teardown for class """
