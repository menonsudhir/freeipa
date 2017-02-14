'''
Test cases for SSSD container Testing with IPA.
################################################################
Note: Make sure PermitRootLogin and PasswordAuthentication is
enabled on atomic host client machine in order to run the below
tests.
Also, we use a static IPA server : 10.76.33.240 to bypass CI 
limitation of not simultaneously supporting RHEL Non-Atomic system
and RHEL Atomic host during provisioning.Credentials to
IPA master: root / Secret123.
###############################################################
'''
import pytest
from ipa_pytests.shared.utils import service_control


class Testmaster(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print"MASTER: ", multihost.master.hostname
        print"CLIENT: ", multihost.client.hostname

    def test_0001_Prerequiste(self, multihost):
        """Taking back up of resolv.conf in order to update it with
        IPA server details. Also creating client installation parametr file,
        this file contains the IPA server details and will be invoked while
        installing IPA client using SSSD container."""
        multihost.client.log.info("Taking backup of /etc/resolv.conf")
        contents = multihost.client.get_file_contents('/etc/resolv.conf')
        multihost.client.put_file_contents('/etc/resolv.conf.backup', contents)
        name_server = ('nameserver ' + multihost.master.ip)
        multihost.client.put_file_contents('/etc/resolv.conf', name_server)
        install_options = ('--server=' + multihost.master.hostname +
                           '\n--domain=testrelm.test'
                           '\n--principal admin --password Secret123'
                           '\n--force-join')
        multihost.client.put_file_contents('/etc/sssd/ipa-client-install-options',
                                           install_options)

    def test_0002_Setup_Install_Client(self, multihost):
        """Installing IPA client with SSSD container image.
        Also verifying if client installation was successful."""
        check1 = multihost.client.run_command('atomic install rhel7/sssd',
                                              raiseonerr=False)
        if check1.returncode == 0:
            print "IPA client install successfull."
        else:
            pytest.fail("IPA client install not successful.")
        if not multihost.client.transport.file_exists('/etc/systemd/system/sssd.service'):
            pytest.fail('SSSD service file not found, kindly debug')
        multihost.client.qerun(['systemctl', 'restart', 'sssd'],
                               exp_returncode=0)

    def test_0003_Kinit_works_for_Client(self, multihost):
        """Verifying that Klist and Kinit command works."""
        cmd1 = multihost.client.run_command(['docker', 'exec', '-i', 'sssd',
                                             'kinit', 'admin'],
                                            stdin_text='Secret123',
                                            set_env=False,
                                            raiseonerr=False)
        print(cmd1.stdout_text)
        assert cmd1.returncode == 0
        multihost.client.qerun(['docker', 'exec', 'sssd', 'klist'],
                               exp_returncode=0)
        multihost.client.qerun(['docker', 'exec', 'sssd', 'kdestroy'],
                               exp_returncode=0)
        # Again verifying that new ticket gets generated after kdestroy.
        cmd2 = multihost.client.run_command(['docker', 'exec', '-i', 'sssd',
                                             'kinit', 'admin'],
                                            stdin_text='Secret123',
                                            set_env=False,
                                            raiseonerr=False)
        print(cmd2.stdout_text)
        assert cmd2.returncode == 0
        multihost.client.qerun(['docker', 'exec', 'sssd', 'klist'],
                               exp_returncode=0)

    def test_0004_SSH_Client(self, multihost):
        """Verifying if ssh access is poosible for client"""
        cmd1 = 'ssh -o GSSAPIAuthentication=yes admin@'
        cmd = multihost.client.run_command(cmd1 + '`hostname`' + ' whoami',
                                            stdin_text='Secret123',
                                            raiseonerr=False)
        assert cmd.returncode == 0
        print(cmd.stdout_text)

    def test_0005_Uninstall_Client(self, multihost):
        """Testing if IPA client can be uninstalled."""
        multihost.client.qerun(['atomic', 'uninstall', 'rhel7/sssd'],
                               exp_returncode=0)

    def class_teardown(self, multihost):
        pass
