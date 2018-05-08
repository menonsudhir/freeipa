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
from ipa_pytests.qe_install import setup_client_docker, uninstall_client_docker
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
        time.sleep(30)
        multihost.master.run_command(['docker', 'images'])

    def test_master_0001(self, multihost):
        """@TITLE: IDM-IPA-TC : ipa-server-docker : Check IPA master Install using docker image"""
        setup_master_docker(multihost.master)
        time.sleep(120)

    def test_master_0002(self, multihost):
        """@TITLE: IDM-IPA-TC : ipa-server-docker : Check Atomic host and docker image details"""
        cmd = multihost.master.run_command(['atomic', 'host', 'status'])
        print cmd.stdout_text
        cmd = multihost.master.run_command(['docker', 'inspect', 'rhel7/ipa-server'])
        print cmd.stdout_text

    def test_master_0003(self, multihost):
        """@TITLE: IDM-IPA-TC : ipa-server-docker : Check if correct version IPA master version is available with IPA image."""
        master = multihost.master
        container = 'ipadocker'
        docker_get_version(master, container)
        docker_service_status(master, container)

    def test_master_0004(self, multihost):
        """@TITLE: IDM-IPA-TC : ipa-server-docker : Check IPA service can be restarted on IPA server configurred with with IPA image."""
        master = multihost.master
        container = 'ipadocker'
        docker_service_status(master, container)
        docker_service_restart(master, container)
        docker_service_status(master, container)

    def test_master_0005(self, multihost):
        """@TITLE: IDM-IPA-TC : ipa-server-docker : Check if Kinit command works on IPA server configurred with with IPA image."""
        master = multihost.master
        container = 'ipadocker'
        docker_kinit_as_admin(master, container)
        docker_klist(master, container)
        docker_kdestroy(master, container)
        docker_klist(master, container)
        docker_kinit_as_admin(master, container)
        docker_klist(master, container)

    def test_master_0006(self, multihost):
        """@TITLE: IDM-IPA-TC : ipa-server-docker : Check if IPA-server configurred using IPa-server image can be uninstalled"""
        master = multihost.master
        uninstall_master_docker(master)

    def class_teardown(self, multihost):
        pass
