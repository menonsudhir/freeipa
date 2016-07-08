'''
Helper functions required for test_kdcproxy
'''
from __future__ import print_function
from ipa_pytests.shared.user_utils import add_ipa_user
import pexpect


def add_user(multihost):
    """
    Add otp user
    """
    # 1. Add IPA user
    add_ipa_user(multihost.master, multihost.testuser, multihost.password)
    multihost.master.kinit_as_user(multihost.testuser, multihost.password)


def mod_otp_user(multihost):
    """
    Modify user
    """
    #   log-in as admin
    multihost.master.kinit_as_admin()
    #   modify new user's authentication type
    multihost.master.qerun(['ipa',
                            'user-mod',
                            '--user-auth-type=otp',
                            multihost.testuser],
                           exp_returncode=0)


def mod_radius_user(multihost):
    """
    Modify user
    """
    #   log-in as admin
    multihost.master.kinit_as_admin()
    #   modify new user's authentication type and assign proxy
    exp_output = 'Modified user "%s"' % multihost.testuser
    multihost.master.qerun(['ipa',
                            'user-mod',
                            '--user-auth-type=radius',
                            multihost.testuser],
                           exp_returncode=0,
                           exp_output=exp_output)
    multihost.master.qerun(['ipa',
                            'user-mod',
                            '--radius=%s' % multihost.radiusproxy,
                            multihost.testuser],
                           exp_returncode=0,
                           exp_output=exp_output)


def add_info(multihost):
    """
    Adding user information in /etc/raddb/users
    """
    with open('/etc/raddb/users', 'a') as f:
        f.write(multihost.testuser + ' Cleartext-Password := "Secret123"\n')


def add_otptoken(multihost):
    """
    Add otptoken to new user
    """
    multihost.master.qerun(
        [
            'ipa',
            'otptoken-add',
            '--type=totp',
            '--no-qrcode',
            '--owner=%s' %
            multihost.testuser,
            '%s' %
            multihost.token],
        exp_returncode=0,
        exp_output='Unique ID: %s' %
        multihost.token)
    print ("########### OTPtoken added to new user successfully ###########\n")


def add_radiusproxy(multihost):
    """
    Add radius proxy server to new user
    """
    multihost.master.kinit_as_admin()
    cmd = 'ipa radiusproxy-add  %s --server=127.0.0.1 ' % multihost.radiusproxy
    proc = pexpect.spawn(cmd)
    proc.logfile = open(multihost.log, "w")
    proc.expect("Secret:")
    proc.sendline(multihost.password)
    proc.expect("Enter Secret again to verify:")
    proc.sendline(multihost.password)
    proc.expect('Added RADIUS proxy server "%s"' % multihost.radiusproxy)
    proc.expect(pexpect.EOF)
    print_output(multihost.log)
    proc.close()
    print ("########### radius proxy added successfully ###########\n")


def delete_otptoken(multihost):
    """
    Deleting token
    """
    multihost.master.qerun(['ipa',
                            'otptoken-del',
                            multihost.token],
                           exp_returncode=0,
                           exp_output='Deleted OTP token "{}"'
                           .format(multihost.token))


def user_login(multihost):
    """
    user login (with manually enabled FAST)
    """
    multihost.master.qerun(['kdestroy', '-A'], exp_returncode=0)
    multihost.master.qerun(
        ['kswitch', '-c', 'KEYRING:persistent:0:0'], exp_returncode=0)
    multihost.master.kinit_as_admin()
    cmd = 'kinit -T KEYRING:persistent:0:0 %s ' % multihost.testuser
    proc = pexpect.spawn(cmd)
    proc.logfile = open(multihost.log, "w")
    proc.expect("Enter OTP Token Value:")
    proc.sendline(multihost.secret)
    proc.expect(pexpect.EOF)
    print_output(multihost.log)
    proc.close()
    print ("\n########### User login successfully ###########\n")


def user_failed_login(multihost):
    """
    User login with expected error.
    """
    multihost.master.qerun(['kdestroy', '-A'], exp_returncode=0)
    multihost.master.qerun(
        ['kswitch', '-c', 'KEYRING:persistent:0:0'], exp_returncode=0)
    multihost.master.kinit_as_admin()
    cmd1 = 'kinit -T KEYRING:persistent:0:0 %s ' % multihost.testuser
    proc = pexpect.spawn(cmd1)
    proc.logfile = open(multihost.log, "w")
    proc.expect("Enter OTP Token Value:")
    proc.sendline(multihost.secret)
    proc.expect(multihost.expectederror)
    print_output(multihost.log)
    proc.close()


def verify_user_login(multihost):
    """
    Verify user login
    """
    cmd = 'klist'
    proc = pexpect.spawn(cmd)
    proc.logfile = open(multihost.log, "w")
    proc.expect('principal: %s' % multihost.testuser)
    proc.expect(pexpect.EOF)
    print_output(multihost.log)
    proc.close()
    print ("\n########### kinit successfully ###########\n")


def print_output(multihost):
    """
    Printing pexpect outputs
    """
    print("########### Log file  ###########")
    with open(multihost, 'r') as f:
        print (f.read())


def delete_radiusproxy(multihost):
    """
    Cleaning user details
    """
    multihost.master.qerun(
        [
            'ipa',
            'radiusproxy-del',
            multihost.radiusproxy],
        exp_returncode=0,
        exp_output='Deleted RADIUS proxy server "%s"' %
        multihost.radiusproxy)

    raddb_bk_file = '/etc/raddb/users_automation_bkp'
    raddb_restore = multihost.master.get_file_contents(raddb_bk_file)
    multihost.master.put_file_contents('/etc/raddb/users', raddb_restore)
