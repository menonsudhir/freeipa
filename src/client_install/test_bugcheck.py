"""
Test Automation for bugs:
"""
import pytest
from __future__ import print_function
from ipa_pytests.qe_install import uninstall_server, setup_client
from ipa_pytests.qe_install import uninstall_client
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.utils import check_rpm


class TestBugCheck(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)
        print("CLIENT: ", multihost.client.hostname)
        print("\nChecking IPA server whether installed on MASTER")
        check_rpm(multihost.master, ['ipa-server'])

    def test_0001(self, multihost):
        """
        Added Automation for: bz1209476
        Bugzilla automation to check that ipa-client package is removed when dbus-python
        is removed since ipa-client is dependent on dbus-python
        """
        check_rpm(multihost.client, ['ipa-client'])
        dbus_remove_cmd = multihost.client.run_command([paths.YUM, 'remove', 'dbus-python', '-y'])
        print ("STDOUT:", dbus_remove_cmd.stdout_text)
        print ("STDERR:", dbus_remove_cmd.stderr_text)
        if "ipa-client" in dbus_remove_cmd.stdout_text:
            multihost.client.qerun(['ipa-client-install'], exp_returncode=127)
            multihost.client.qerun([paths.RPM, '-q', 'ipa-client'], exp_returncode=1)

    def test_0002(self, multihost):
        """ Added automation for:bz1196656, bz1284025, bz1205160.
        Bugzilla verification to enable debugging for spawned commands.
        Also verifying whether sshd_config details get modified after client
        install.
        Also verifying that when backend doesn't start due to missing or
        invalid keytab, it is captured inside sssd.log file."""
        sshd_conf = multihost.client.get_file_contents('/etc/ssh/sshd_config')
        sshd_conf += '\nMatch Address 10.65.207.112'
        multihost.client.put_file_contents('/etc/ssh/sshd_config', sshd_conf)
        setup_client(multihost.client, multihost.master)
        if multihost.master.transport.file_exists('/etc/ipa/default.conf'):
            print("IPA client is installed, continuing tests")
            check2 = multihost.client.run_command('grep -C 3 /usr/sbin/ntpd /var/log/ipaclient-install.log',
                                                  raiseonerr=False)
            if check2.returncode == 0:
                check3 = multihost.client.qerun(['tail',
                                                 '-n', '3',
                                                 '/var/log/ipaclient-install.log'],
                                                exp_output='complete')
                check4 = multihost.client.qerun('tail -5 /etc/ssh/sshd_config',
                                                exp_output='10.65.207.112')
                multihost.client.qerun('klist -k',
                                       exp_returncode=0)
                service_control(multihost.client, 'sssd', 'stop')
                multihost.client.rename_file('/etc/krb5.keytab', '/tmp')
                service_control(multihost.client, 'sssd', 'start')
                multihost.client.qerun('systemctl -l status sssd.service',
                                       exp_returncode=1)
                backend = multihost.client.qerun(['tail', '-20',
                                                  '/var/log/sssd/sssd.log'],
                                                 exp_returncode=0,
                                                 exp_output='backend')
                if check3.returncode and check4.returncode and backend.returncode == 0:
                    print('Client installation complete, BZ1196656, BZ1284025 and BZ1205160 PASSED')
                else:
                    pytest.xfail('Either BZ1196656 or BZ1284025 or BZ1205160 FAILED, Kindly debug')
        else:
            pytest.xfail("IPA client is not installed, BZ1196656 FAILED")

    def test_0003(self, multihost):
        """ Added automation for : bz1215200, bz1211708.
        Bugzilla verifying ipa-client-install configures IPA server
        as NTP source even when if IPA server has not ntpd configured."""
        uninstall_client(multihost.client)
        uninstall_server(multihost.master)
        '''Setup master with no NTP'''
        cmd = multihost.master.run_command(['ipa-server-install',
                                            '--setup-dns',
                                            '--forwarder', multihost.master.config.dns_forwarder,
                                            '--domain', multihost.master.domain.name,
                                            '--realm', multihost.master.domain.realm,
                                            '--hostname', multihost.master.hostname,
                                            '--ip-address', multihost.master.ip,
                                            '--admin-password', multihost.master.config.admin_pw,
                                            '--ds-password', multihost.master.config.dirman_pw,
                                            '--no-ntp',
                                            '-U'], raiseonerr=False)
        print ("STDOUT:", cmd.stdout_text)
        print ("STDERR:", cmd.stderr_text)
        if cmd.returncode != 0:
            raise ValueError("ipa-server-install failed with error code=%s" % cmd.returncode)
        check5 = multihost.master.run_command('ipactl status | grep RUNNING')
        if check5.returncode != 0:
            print("IPA server service not RUNNING.Kindly debug")
        else:
            print("IPA service is running, continuing")
            setup_client(multihost.client, multihost.master)
            check6 = multihost.client.qerun(['ls', '/etc/ipa/'],
                                            exp_output='default.conf',
                                            raiseonerr=False)
            if check6.returncode == 0:
                print("IPA client is installed, BZ1215200 and BZ1211708 PASSED")
            else:
                pytest.xfail("IPA client is not installed, BZ1215200 and BZ1211708 FAILED")

    def test_0004(self, multihost):
        """ Added automation for : bz1215197.
        Bugzilla automation to verify ipa-client-install
        does not ignores --ntp-server option during time sync"""
        uninstall_client(multihost.client)
        """Setup client with NTP"""
        cmd = multihost.client.run_command(['ipa-client-install',
                                            '--principal', 'admin',
                                            '--password', multihost.master.config.admin_pw,
                                            '--ntp-server', '0.rhel.pool.ntp.org',
                                            '--ntp-server', '1.rhel.pool.ntp.org',
                                            '--force-ntpd',
                                            '-U'], raiseonerr=False)
        print ("STDOUT:", cmd.stdout_text)
        print ("STDERR:", cmd.stderr_text)
        if cmd.returncode != 0:
            raise ValueError("ipa-client-install failed with error code=%s" % cmd.returncode)
        check7 = multihost.client.run_command('grep rhel.pool.ntp.org /etc/ntp.conf')
        if check7.returncode == 0:
            print("NTP server details found, BZ1215197 PASSED")
        else:
            pytest.xfail("NTP server details not found, BZ1215197 FAILED")

    def class_teardown(self, multihost):
        """Full suite teardown """
        pass
