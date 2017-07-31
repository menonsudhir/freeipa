'''
Test cases for IPA-server-docker container as IPA.
################################################################
Note: Make sure PermitRootLogin and PasswordAuthentication is
enabled on atomic host client machine in order to run the below
tests.
###############################################################
'''
import pytest
from ipa_pytests.shared.utils import service_control
from ipa_pytests.shared.utils import *
from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.qe_install import *

class Testmaster(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print"MASTER: ", multihost.master.hostname

    def test__master_0001(self, multihost):
        """Check IPA master version, kinit and services."""
        master = multihost.master
        container = 'ipadocker'
        docker_get_version(master, container)
        docker_service_status(master, container)
        docker_service_restart(master, container)
        docker_service_status(master, container)
        docker_kinit_as_admin(master, container)
        docker_klist(multihost.master, container)
        docker_kdestroy(multihost.master, container)
        docker_klist(multihost.master, container)
        docker_kinit_as_admin(master, container)
        docker_klist(multihost.master, container)

    def test__master_0002(self, multihost):
        """ Uninstall Master"""
        master = multihost.master
        uninstall_master_docker(master)

    def class_teardown(self, multihost):
        pass
