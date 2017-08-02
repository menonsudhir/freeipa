'''
Test cases for SSSD container Testing with IPA.
################################################################
Note: Make sure PermitRootLogin and PasswordAuthentication is
enabled on atomic host client machine in order to run the below
tests.
###############################################################
'''
import pytest
from ipa_pytests.shared.utils import *
from ipa_pytests.qe_install import setup_client_docker, uninstall_client_docker

class Testmaster(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print"MASTER: ", multihost.master.hostname
        print"CLIENT: ", multihost.client.hostname

    def test_0001_Install_Client(self, multihost):
        """Install IPA client using sssd-container"""
        print("Runing ipa_client_docker")
        client = multihost.client
        master = multihost.master
        setup_client_docker(client, master)

    def test_0002_Kinit_works_for_Client(self, multihost):
        """Verifying that Klist and Kinit command works."""
        client = multihost.client
        container = 'sssd'
        docker_get_version(client, container)
        docker_kinit_as_admin(client, container)
        docker_klist(client, container)
        docker_kdestroy(client, container)
        docker_klist(client, container)
        docker_kinit_as_admin(client, container)
        docker_klist(client, container)

    def test_0003_SSH_Client(self, multihost):
        """Verifying if ssh access is poosible for client"""
        cmd1 = 'ssh -o GSSAPIAuthentication=yes admin@'
        cmd = multihost.client.run_command(cmd1 + '`hostname`' + ' whoami',
                                           stdin_text='Secret123',
                                           raiseonerr=False)
        assert cmd.returncode == 0
        print(cmd.stdout_text)

    def test_0004_Uninstall_Client(self, multihost):
        """ Uninstall Client"""
        client = multihost.client
        uninstall_client_docker(client)

    def class_teardown(self, multihost):
        pass
