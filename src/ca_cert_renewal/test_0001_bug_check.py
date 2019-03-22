""" Bugzilla automation"""
from time import sleep
import pytest
from ipa_pytests.qe_class import multihost
import ipa_pytests.shared.paths as paths
from ipa_pytests.qe_install import setup_master, uninstall_server


class TestBugCheck(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        multihost.realm = multihost.master.domain.realm

        print("Using following hosts for CA Cert Renewal testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("*" * 80)

    def test_bug_964130(self, multihost):
        """Check if trust attributes doesn't change after renewal

        This test checks if trust attributes doesn't get change.
        related ticket : https://bugzilla.redhat.com/show_bug.cgi?id=964130
        """
        setup_master(multihost.master)

        # trust attribute before renewal
        cmd = multihost.master.run_command(['certutil', '-L', '-d',
                                            paths.PKIALIASDB, '|',
                                            'grep', 'pki'])
        trust_attr_before_renew = cmd.stdout_text

        # change system date to trigger the certificate renewal
        multihost.master.run_command(['date', '-s', '719days'])
        sleep(300)

        # trust attribute after renewal
        cmd = multihost.master.run_command(['certutil', '-L', '-d',
                                            paths.PKIALIASDB, '|',
                                            'grep', 'pki'])

        # check if trust attributes didn't got changed
        lines = iter(trust_attr_before_renew.splitlines())
        for line in lines:
            assert line in cmd.stdout_text
        print("BZ964130 not found. Trusts attibutes are not changed after renewal")

        # uninstall master
        uninstall_server(multihost.master)

    def class_teardown(self, multihost):
        """ Teardown for class """
        pass
