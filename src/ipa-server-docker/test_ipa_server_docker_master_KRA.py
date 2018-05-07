'''
Test cases for IPA-server-docker container as IPA.
################################################################
Note: Make sure PermitRootLogin and PasswordAuthentication is
enabled on atomic host client machine in order to run the below
tests.
###############################################################
'''
import pytest
import time
from ipa_pytests.shared.utils import service_control
from ipa_pytests.shared.utils import *
from ipa_pytests.qe_install import setup_master_docker, uninstall_master_docker
from ipa_pytests.qe_install import setup_replica_docker, uninstall_replica_docker
from ipa_pytests.qe_install import setup_kra_docker
from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.qe_install import *


class TestMaster(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print"MASTER: ", multihost.master.hostname
        # Enabling Setsebool, this change is required or else
        # installation will fail. This is introduced from
        # RHEL Atomic host 7.5.0 onwards.
        multihost.master.run_command(['setsebool', '-P',
                                      'container_manage_cgroup',
                                      '1'],  raiseonerr=False)
        multihost.master.run_command(['getsebool', 'container_manage_cgroup'],
                                      raiseonerr=False)
        time.sleep(60)
        multihost.master.run_command(['docker', 'images'])

    def test_master_0001(self, multihost):
        """@TITLE: IDM-IPA-TC : ipa-server-docker : Check if KRA can be installed on IPA master using docker image"""
        master = multihost.master
        container = 'ipadocker'
        setup_master_docker(master)
        time.sleep(120)
        setup_kra_docker(master, container)
        docker_service_restart(master, container)
        docker_service_status(master, container)
        docker_kinit_as_admin(master, container)

    def class_teardown(self, multihost):
        """ Thie is Teardown"""
        master = multihost.master
        uninstall_master_docker(master)
        pass
