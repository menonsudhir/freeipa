"""
Overview:
This is a quick tests for IPA Master and Replica
"""

import time
import pytest
from ipa_pytests.qe_install import (setup_master, setup_replica,
                                    uninstall_server)
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.shared import paths
from ipa_pytests.shared.utils import check_mod_ssl_migration


class Testmaster1(object):
    """ Test Class """

    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print("MASTER: %s" % multihost.master.hostname)
        print("REPLICA: %s" % multihost.replicas[0].hostname)

    def test_0001_mod_ssl_check(self, multihost):
        """
        IDM-IPA-TC:check_mod_ssl:Verifiying mod_ssl
        after IPA Master and Replica installation
        """
        print("\nChecking IPA server whether installed on MASTER")
        cmd = multihost.master.run_command([paths.RPM, '-q', 'ipa-server'],
                                           set_env=False, raiseonerr=False)
        if cmd.returncode == 0:
            print("IPA server package found on MASTER")
            ipactl_check1 = multihost.master.run_command(
                'ipactl status | grep RUNNING', raiseonerr=False)
            if ipactl_check1.returncode != 0:
                print("IPA server service not RUNNING, thus setup ipa-server")
                setup_master(multihost.master, setup_reverse=False)
            else:
                print("IPA service is running")
        else:
            print("\n IPA server package not found on MASTER, thus installing")
            install1 = multihost.master.run_command(
                ['dnf', '-y', 'module', 'install', 'idm:4/dns'])
            if install1.returncode == 0:
                print("IPA server package installed.")
                print("Setting up ipa-server on MASTER")
                setup_master(multihost.master, setup_reverse=False)
            else:
                pytest.fail('IPA server package installation failed, check'
                            'repo links for further debugging')
        print("checking for migration of mod_ssl from mod_nss on MASTER")
        check_mod_ssl_migration(multihost.master)

        print("checking ipactl status on replica")
        ipactl_check2 = multihost.replicas[0].run_command(
            'ipactl status | grep RUNNING', raiseonerr=False)
        if ipactl_check2.returncode != 0:
            print("IPA server service not RUNNING on REPLICA")
            print("Setting up REPLICA")
            setup_replica(multihost.replicas[0], multihost.master,
                          setup_reverse=False)
        else:
            print("IPA service is running on REPLICA")
        print("checking for migration of mod_ssl from mod_nss on REPLICA")
        check_mod_ssl_migration(multihost.replicas[0])

    def class_teardown(self, multihost):
        """ Full suite teardown """
        print("CLASS_TEARDOWN")
        print("MASTER: ", multihost.master.hostname)
        print("REPLICA: ", multihost.replicas[0].hostname)
        uninstall_server(multihost.master)
        uninstall_server(multihost.replicas[0])
