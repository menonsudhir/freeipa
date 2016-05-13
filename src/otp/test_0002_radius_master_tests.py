"""
Radius testcases
"""
from .lib import (add_user, add_radiusproxy,
                  mod_radius_user, add_info, user_login,
                  verify_user_login, delete_radiusproxy,
                  user_failed_login, print_output)
import ipa_pytests.shared.utils as shared_utils
import os
import pexpect


class TestRadiusfunction(object):
    """ Test Class """

    def class_setup(self, multihost):
        """ Setup for class """

        list_of_packages = ['freeradius', 'freeradius-ldap', 'freeradius-utils']

        multihost.master.yum_install(list_of_packages)

        multihost.realm = multihost.master.domain.realm
        multihost.password = "testing123"
        multihost.secret = 'Secret123'
        multihost.log = "/tmp/log_radius"
        raddb_bkp = multihost.master.get_file_contents('/etc/raddb/users')
        multihost.master.put_file_contents\
            ('/etc/raddb/users_automation_bkp', raddb_bkp)

    def test_radius_0001(self, multihost):
        """
        IDM-IPA-TC: OTP: User login with a radius authentication
        """
        multihost.radiusproxy = "radiusproxy01"
        multihost.testuser = 'radiususer'

        # add otp user
        add_user(multihost)

        # add radius proxy
        add_radiusproxy(multihost)

        # modify otp user as admin
        mod_radius_user(multihost)

        # Add info
        add_info(multihost)

        # Start radius server
        multihost.master.qerun(['service', 'radiusd', 'start'])

        # Log-in as user with manually enabled FAST
        user_login(multihost)

        # Verify log-in
        verify_user_login(multihost)

        # cleanup
        shared_utils.delete_user(multihost)
        delete_radiusproxy(multihost)

        # Stoping radius server
        multihost.master.qerun(['killall', '-sKILL', 'radiusd'])

    def test_radius_0002(self, multihost):
        """
        IDM-IPA-TC: OTP: User login without starting radius server
        """
        multihost.radiusproxy = "radiusproxy02"
        multihost.testuser = 'radiususer02'
        multihost.expectederror = "reauthentication failed while " \
                                  "getting initial credentials"

        # add otp user
        add_user(multihost)

        # add radius proxy
        add_radiusproxy(multihost)

        # modify otp user as admin
        mod_radius_user(multihost)

        # Add info
        add_info(multihost)

        # User login with manually enabled FAST
        user_failed_login(multihost)

        # cleanup
        shared_utils.delete_user(multihost)
        delete_radiusproxy(multihost)

    def test_radius_0003(self, multihost):
        """
        IDM-IPA-TC: OTP: User login with a radius
        authentication with wrong secret key
        """
        multihost.radiusproxy = "radiusproxy03"
        multihost.testuser = "radiususer03"
        multihost.expectederror = "reauthentication failed while " \
                                  "getting initial credentials"

        # add otp user
        add_user(multihost)

        # add radius proxy
        add_radiusproxy(multihost)

        # modify otp user as admin
        mod_radius_user(multihost)

        # Add info
        add_info(multihost)

        # Start radius server
        multihost.master.qerun(['service', 'radiusd', 'start'])

        # User login with manually enabled FAST
        multihost.wrongsecret = "wrongPassword"
        multihost.master.qerun(['kdestroy', '-A'], exp_returncode=0)
        multihost.master.qerun(
            ['kswitch', '-c', 'KEYRING:persistent:0:0'], exp_returncode=0)
        multihost.master.kinit_as_admin()
        cmd = 'kinit -T KEYRING:persistent:0:0 %s ' % multihost.testuser
        proc = pexpect.spawn(cmd)
        proc.logfile = open(multihost.log, "w")
        proc.expect("Enter OTP Token Value:")
        proc.sendline(multihost.wrongsecret)
        proc.expect(multihost.expectederror)
        proc.expect(pexpect.EOF)
        print_output(multihost.log)
        proc.close()

        # cleanup
        shared_utils.delete_user(multihost)
        delete_radiusproxy(multihost)

        # Stoping radius server
        multihost.master.qerun(['killall', '-sKILL', 'radiusd'])

    def test_radius_0004(self, multihost):
        """
        IDM-IPA-TC: OTP: Delete radiusproxy as user
        """
        multihost.radiusproxy = "radiusproxy04"
        multihost.testuser = 'radiususer'

        # add otp user
        add_user(multihost)

        # add radius proxy
        add_radiusproxy(multihost)

        # modify otp user as admin
        mod_radius_user(multihost)

        # Add info
        add_info(multihost)

        # Start radius server
        os.system("radiusd -s&")
#        multihost.master.qerun(['radiusd', '-s'])

        # Log-in as user with manually enabled FAST
        user_login(multihost)

        # Verify log-in
        verify_user_login(multihost)

        # Delete radius server as user
        multihost.master.qerun(['ipa',
                                'radiusproxy-del',
                                multihost.radiusproxy],
                               exp_returncode=1,
                               exp_output='ipa: ERROR: Insufficient access:')
        print "\n########### radius Proxy not deleted ###########\n"

        # cleanup
        shared_utils.delete_user(multihost)
        delete_radiusproxy(multihost)

        # Stoping radius server
        multihost.master.qerun(['killall', '-sKILL', 'radiusd'])

    def test_radius_0005(self, multihost):
        """
        IDM-IPA-TC: OTP: Delete radiusproxy as admin
        """
        multihost.radiusproxy = "radiusproxy05"
        multihost.testuser = 'radiususer05'

        # Add radius proxy
        add_radiusproxy(multihost)

        # Delete radius proxy as admin
        cmd = 'ipa radiusproxy-del  %s ' % multihost.radiusproxy
        proc = pexpect.spawn(cmd)
        proc.logfile = open(multihost.log, "w")
        proc.expect('Deleted RADIUS proxy server "%s"' % multihost.radiusproxy)
        proc.expect(pexpect.EOF)
        print_output(multihost.log)
        proc.close()
        print "########### radius proxy deleted successfully ###########\n"

    def test_radius_0006(self, multihost):
        """
        IDM-IPA-TC: OTP: Modify- Rename radiusproxy with existing proxy name
        """

        users = ['radiusproxy06', 'radiusproxy061']

        for each_user in users:
            multihost.radiusproxy = each_user
            add_radiusproxy(multihost)

        cmd = 'ipa radiusproxy-mod --rename=%s' % users[1]
        proc = pexpect.spawn(cmd)
        proc.logfile = open(multihost.log, "w")
        proc.expect('RADIUS proxy server name:')
        proc.sendline(users[0])
        proc.expect('ipa: ERROR: This entry already exists')
        proc.expect(pexpect.EOF)
        print_output(multihost.log)
        proc.close()

#        multihost.radiusproxy = users[0]
        for each_user in users:
            multihost.radiusproxy = each_user
            delete_radiusproxy(multihost)

    def test_radius_0007(self, multihost):
        """
        IDM-IPA-TC: OTP: Modify- Rename radius proxy with new proxy name
        """
        users = ['radiusproxy07', 'radiusproxy071']

        # Aadd radius proxy
        multihost.radiusproxy = users[1]
        add_radiusproxy(multihost)

        # Modify radius proxy
        cmd = 'ipa radiusproxy-mod --rename=%s' % users[0]
        proc = pexpect.spawn(cmd)
        proc.logfile = open(multihost.log, "w")
        proc.expect('RADIUS proxy server name:')
        proc.sendline(multihost.radiusproxy)
        proc.expect('Modified RADIUS proxy server "%s"' % users[1])
        proc.expect(pexpect.EOF)
        print_output(multihost.log)
        proc.close()
        print "########### radius proxy rename successfully ###########\n"

        # Cleanup
        multihost.radiusproxy = users[0]
        delete_radiusproxy(multihost)

    def test_radius_0008(self, multihost):
        """
        IDM-IPA-TC: OTP: Modify- Rename with wrong radiusproxy
        """
        multihost.wrongradiusproxy = "radiusproxy081"
        multihost.radiusproxy = "radiusproxy08"

        # Aadd radius proxy
        add_radiusproxy(multihost)
        multihost.master.qerun(['ipa',
                                'radiusproxy-mod',
                                '%s' % multihost.wrongradiusproxy],
                               exp_returncode=2,
                               exp_output="RADIUS proxy server not found")

        # cleanup
        delete_radiusproxy(multihost)

    def test_radius_0009(self, multihost):
        """
        IDM-IPA-TC: OTP: Modify- Add timeout and retries
        """
        multihost.radiusproxy = "radiusproxy09"

        # Aadd radius proxy
        add_radiusproxy(multihost)
        multihost.master.qerun(
            [
                'ipa',
                'radiusproxy-mod',
                '%s' %
                multihost.radiusproxy,
                '--timeout=10',
                '--retries=10'],
            exp_returncode=0,
            exp_output='Modified RADIUS proxy server "%s"' %
            multihost.radiusproxy)

        # cleanup
        delete_radiusproxy(multihost)

    def test_radius_0010(self, multihost):
        """
        IDM-IPA-TC: OTP: Modify- Retries with higher value
        """
        multihost.radiusproxy = "radiusproxy010"

        # Aadd radius proxy
        add_radiusproxy(multihost)
        multihost.master.qerun(['ipa',
                                'radiusproxy-mod',
                                '%s' % multihost.radiusproxy,
                                '--retries=100'],
                               exp_returncode=1,
                               exp_output='ipa: ERROR: invalid '
                               'retries'
                               ': can be at most 10')
        # cleanup
        delete_radiusproxy(multihost)

    def test_radius_0011(self, multihost):
        """
        IDM-IPA-TC: OTP: Modify- Timeout with higher value
        """
        multihost.radiusproxy = "radiusproxy011"

        # Add radius proxy
        add_radiusproxy(multihost)
        multihost.master.qerun(['ipa',
                                'radiusproxy-mod',
                                '%s' % multihost.radiusproxy,
                                '--timeout=2147483650'],
                               exp_returncode=1,
                               exp_output='ipa: ERROR: invalid '
                               'timeout'
                               ': can be at most 2147483647')
        # cleanup
        delete_radiusproxy(multihost)

    def test_radius_0012(self, multihost):
        """
        IDM-IPA-TC: OTP: Modify- Find radius proxy as admin
        """
        multihost.radiusproxy = "radiusproxy012"

        # Aadd radius proxy
        add_radiusproxy(multihost)
        # Find radius proxy
        multihost.master.qerun(['ipa',
                                'radiusproxy-find'],
                               exp_returncode=0,
                               exp_output='RADIUS proxy servers matched')
        # cleanup
        delete_radiusproxy(multihost)

    def test_radius_0013(self, multihost):
        """
        IDM-IPA-TC: OTP: Modify- Show radius proxy as admin
        """
        multihost.radiusproxy = "radiusproxy013"

        # Add radius proxy
        add_radiusproxy(multihost)
        # show radius proxy
        multihost.master.qerun(
            [
                'ipa',
                'radiusproxy-show',
                '%s' %
                multihost.radiusproxy],
            exp_returncode=0,
            exp_output='RADIUS proxy server name: "%s"' %
            multihost.radiusproxy)
        # cleanup
        delete_radiusproxy(multihost)

    def test_radius_0014(self, multihost):
        """
        IDM-IPA-TC: OTP: Modify- Show radius proxy as user
        """
        multihost.radiusproxy = "radiusproxy014"
        multihost.testuser = 'radiususer'

        # add otp user
        add_user(multihost)

        # add radius proxy
        add_radiusproxy(multihost)

        # modify otp user as admin
        mod_radius_user(multihost)

        # Add info
        add_info(multihost)

        # Start radius server
        multihost.master.qerun(['service', 'radiusd', 'start'])

        # Log-in as user with manually enabled FAST
        user_login(multihost)

        # Verify log-in
        verify_user_login(multihost)

        # show radius proxy
        multihost.master.qerun(
            [
                'ipa',
                'radiusproxy-show',
                '%s' %
                multihost.radiusproxy],
            exp_returncode=2,
            exp_output='ipa: ERROR: %s: RADIUS proxy server not found' %
            multihost.radiusproxy)
        # cleanup
        shared_utils.delete_user(multihost)
        delete_radiusproxy(multihost)

        # Stoping radius server
        multihost.master.qerun(['killall', '-sKILL', 'radiusd'])

    def test_radius_0015(self, multihost):
        """
        IDM-IPA-TC: OTP: Modify- Find radius proxy as user
        """
        multihost.radiusproxy = "radiusproxy015"
        multihost.testuser = 'radiususer'

        # add otp user
        add_user(multihost)

        # add radius proxy
        add_radiusproxy(multihost)

        # modify otp user as admin
        mod_radius_user(multihost)

        # Add info
        add_info(multihost)

        # Start radius server
        multihost.master.qerun(['service', 'radiusd', 'start'])

        # Log-in as user with manually enabled FAST
        user_login(multihost)

        # Verify log-in
        verify_user_login(multihost)

        # show radius proxy
        multihost.master.qerun(['ipa',
                                'radiusproxy-find',
                                '%s' % multihost.radiusproxy],
                               exp_returncode=1,
                               exp_output='0 RADIUS proxy servers matched')
        # cleanup
        shared_utils.delete_user(multihost)
        delete_radiusproxy(multihost)

        # Stoping radius server
        multihost.master.qerun(['killall', '-sKILL', 'radiusd'])

    def class_teardown(self, multihost):
        """ Teardown for class """
        os.system('mv -f /etc/raddb/users_automation_bkp /etc/raddb/users')
