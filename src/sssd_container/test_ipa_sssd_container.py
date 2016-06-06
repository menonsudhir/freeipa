'''
Test cases for SSSD container Testing with IPA.
################################################################
Note: Make sure PermitRootLogin and PasswordAuthentication is
enabled on atomic host client machine in order to run the below
tests.
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
        contents = multihost.client.get_file_contents('/etc/sysconfig/docker')
        multihost.client.put_file_contents('/etc/sysconfig/docker.orig',
                                           contents)
        multihost.client.transport.remove_file('/etc/sysconfig/docker')
        docker_file='''# /etc/sysconfig/docker
                    \nOPTIONS='--selinux-enabled'
                    \nDOCKER_CERT_PATH=/etc/docker
                    \nADD_REGISTRY='--add-registry registry.access.stage.redhat.com'
                    \nINSECURE_REGISTRY='--insecure-registry registry.access.stage.redhat.com'
                    \n"/etc/sysconfig/docker"'''
        multihost.client.put_file_contents('/etc/sysconfig/docker',
                                           docker_file)
        cmd = multihost.client.run_command('systemctl restart docker')
        print cmd.stdout_text
        print cmd.stderr_text

    def test_0001(self, multihost):
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

    def test_0002(self, multihost):
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

    def test_0003(self, multihost):
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

    def test_004(self, multihost):
        """Testing if IPA client can be uninstalled."""
        multihost.client.qerun(['atomic', 'uninstall', 'rhel7/sssd'],
                               exp_returncode=0)

    def class_teardown(self, multihost):
        pass
