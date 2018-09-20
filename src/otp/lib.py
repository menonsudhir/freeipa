'''
Helper functions required for test_kdcproxy
'''

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
    expect_script = 'set timeout 15\n'
    expect_script += 'spawn ipa radiusproxy-add %s --server=127.0.0.1\n' % multihost.radiusproxy
    expect_script += 'expect "Secret:"\n'
    expect_script += 'send "%s\r"\n' % multihost.password
    expect_script += 'expect "Enter Secret again to verify:"\n'
    expect_script += 'send "%s\r"\n' % multihost.password
    expect_script += 'expect "Added RADIUS proxy server*"\n'
    expect_script += 'expect EOF\n'
    output = multihost.master.expect(expect_script)
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
    expect_script = 'set timeout 15\n'
    expect_script += 'spawn kinit -T KCM:0 %s\n' % multihost.testuser
    expect_script += 'expect "Enter OTP Token Value:"\n'
    expect_script += 'send "%s\r"\n' % multihost.secret
    expect_script += 'expect EOF\n'
    output = multihost.master.expect(expect_script)
    print ("\n########### User login successfully ###########\n")


def user_failed_login(multihost):
    """
    User login with expected error.
    """
    multihost.master.qerun(['kdestroy', '-A'], exp_returncode=0)
    multihost.master.qerun(
        ['kswitch', '-c', 'KEYRING:persistent:0:0'], exp_returncode=0)
    multihost.master.kinit_as_admin()
    expect_script = 'set timeout 15\n'
    expect_script += 'spawn kinit -T KCM:0 %s\n' % multihost.testuser
    expect_script += 'expect "Enter OTP Token Value:"\n'
    expect_script += 'send "%s\r"\n' % multihost.secret
    expect_script += '%s\n' % multihost.expectederror
    output = multihost.master.expect(expect_script)


def verify_user_login(multihost):
    """
    Verify user login
    """
    expect_script = 'set timeout 15\n'
    expect_script += 'spawn klist'
    expect_script += 'expect principal: %s\n' % multihost.testuser
    expect_script += 'expect EOF\n'
    output = multihost.master.expect(expect_script)
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
