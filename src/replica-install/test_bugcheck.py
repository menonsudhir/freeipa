"""
Overview:
IPA replica install bzs automation
#1283890
#1242036
SetUp Requirements:
-Master and Replica on latest version of RHEL OS
-The test use dummy data which is not used in actual installation.
"""

import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.shared import paths
from ipa_pytests.qe_install import setup_master, setup_replica
from ipa_pytests.shared.rpm_utils import check_rpm
from ipa_pytests.shared.utils import (start_firewalld,
                                      stop_firewalld)


class TestBugCheck(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print("REPLICA: ", multihost.replica.hostname)
        print("\nChecking IPA server package whether installed on REPLICA")
        rpm_list = ['ipa-server']
        check_rpm(multihost.replica, rpm_list)

    def test_0001_bz1283890(self, multihost):
        """
        Testcase to validate IPA replica install parameters
        """
        exp_output = "ipa-replica-install: error: option --forwarder:"
        multihost.replica.qerun(['ipa-replica-install', '--forwarder=a.c.b.d'],
                                exp_returncode=2,
                                exp_output=exp_output)

    def test_0002_bz1283890(self, multihost):
        """
        Testcase to validate IPA replica install parameters
        """
        cmd = "ipa-replica-install"
        string = "Configuration of client side components failed"
        cmd1 = multihost.replicas[0].run_command(cmd, raiseonerr=False)
        if cmd1.returncode==1 and string in cmd1.stderr_text:
           print "bz1283890 passed"
        else:
           print "bz1283890 failed"

    def test_0003_bz_1242036(self, multihost):
        """Master is configured using '--setup-dns'
        *.gpg file is installed on replica without using '--setup-dns'
        both master and replica give same output for 'dnsrecord-find testrelm.test'
        in order to verify that SRV DNS records for the replica were added correctly."""
        stop_firewalld(multihost.master)
        stop_firewalld(multihost.replicas[0])
        setup_replica(multihost.replica, multihost.master,
                      setup_dns=True,
                      setup_ca=True)
        multihost.master.kinit_as_admin()
        multihost.replica.kinit_as_admin()
        master_op = multihost.master.run_command(['ipa', 'dnsrecord-find', multihost.master.domain.name])
        multihost.replica.qerun(['ipa', 'dnsrecord-find', multihost.replica.domain.name],
                                exp_returncode=0,
                                exp_output=master_op.stdout_text)

    def class_teardown(self, multihost):
        """ Full suite teardown """
        pass
