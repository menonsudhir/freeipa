"""
Overview:
IPA replica install bzs automation on domain-level 1
#1283890
#1242036
SetUp Requirements:
-Master and Replica on latest version of RHEL OS
-The test use dummy data which is not used in actual installation.
"""

import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_use_class_setup
import os
from ipa_pytests.shared.server_utils import server_del
from ipa_pytests.qe_install import uninstall_server, setup_replica, setup_master
from ipa_pytests.shared.rpm_utils import check_rpm
from ipa_pytests.shared.utils import (start_firewalld,
                                      stop_firewalld)


class TestBugCheck(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        multihost.replica = multihost.replicas[0]
        print("\nClass Setup")
        os.environ['DOMAIN_LEVEL'] = '1'
        print(os.environ['DOMAIN_LEVEL'])
        setup_master(multihost.master,setup_kra=False)
        print("Master: ", multihost.master.hostname)
        print("REPLICA: ", multihost.replica.hostname)
        print("\nChecking IPA server package whether installed on REPLICA")
        cmd = ['dnf', '-y', 'module', 'install', 'idm:4']
        multihost.replica.qerun(cmd, exp_returncode=0)

    def test_0001_bz1283890(self, multihost):
        """
        IDM-IPA-TC : Replica-Install : validate IPA replica install parameter : --forwarder
        """
        exp_output = "ipa-replica-install: error: option --forwarder:"
        multihost.replica.qerun(['ipa-replica-install', '--forwarder=a.c.b.d'],
                                exp_returncode=2,
                                exp_output=exp_output)

    def test_0002_bz1283890(self, multihost):
        """
        IDM-IPA-TC : Replica-Install : validate IPA replica install parameters
        """
        cmd = "ipa-replica-install"
        string = "Configuration of client side components failed"
        cmd1 = multihost.replicas[0].run_command(cmd, raiseonerr=False)
        if cmd1.returncode==1 and string in cmd1.stderr_text:
           print("bz1283890 passed")
        else:
           print("bz1283890 failed")

    def test_0003_bz_1242036(self, multihost):
        """
        IDM-IPA-TC : Replica-Install : Verify SRV DNS records for the replica added correctly
        """
        # Master is configured using '--setup-dns'
        # *.gpg file is installed on replica without using '--setup-dns'
        # both master and replica give same output for 'dnsrecord-find testrelm.test'
        # in order to verify that SRV DNS records for the replica were added correctly.
        uninstall_server(multihost.replica)
        server_del(multihost.master,
                   hostname=multihost.replica.hostname,
                   force=True)
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
        uninstall_server(multihost.replica)
        uninstall_server(multihost.master)

