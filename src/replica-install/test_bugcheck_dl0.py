"""
Overview:
IPA replica install bzs automation on domain-level 0
#1492560
SetUp Requirements:
-Master and Replica on latest version of RHEL OS
-The test use dummy data which is not used in actual installation.
"""

import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.qe_install import uninstall_server, setup_replica, setup_master
from ipa_pytests.shared.server_utils import server_del
from ipa_pytests.shared.rpm_utils import check_rpm
import os


class TestBugCheck(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        multihost.replica = multihost.replicas[0]
        print("\nClass Setup")
        os.environ['DOMAIN_LEVEL'] = '0'
        print(os.environ['DOMAIN_LEVEL'])
        setup_master(multihost.master,setup_kra=True)
        print("Master: ", multihost.master.hostname)
        print(" %s is installed on domain-level 0 " % multihost.master.hostname)
        print("REPLICA: ", multihost.replica.hostname)
        print("\nChecking IPA server package whether installed on REPLICA")
        rpm_list = ['ipa-server']
        check_rpm(multihost.replica, rpm_list)

    def test_0001_bz_1492560(self, multihost):
        """
        IDM-IPA-TC : Replica-Install : Verify replica install with setup-kra at doamin 0
        """
        # Master is configured using --domain-level=0
        # replica is installed using --setup-kra
        # in order to verify ipa-replica is installed successfully
        # using setup-kra at domain level 0
        setup_replica(multihost.replica, multihost.master,
                      setup_dns=True,
                      setup_ca=True, setup_kra=True)

    def class_teardown(self, multihost):
        """ Full suite teardown """
        uninstall_server(multihost.replica)
        server_del(multihost.master,
                   hostname=multihost.replica.hostname,
                   force=True)
        uninstall_server(multihost.master)

