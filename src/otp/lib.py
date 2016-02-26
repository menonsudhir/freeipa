'''
Helper functions required for test_kdcproxy
'''
from __future__ import print_function
from ipa_pytests.shared.utils import add_ipa_user


def add_otp_user(multihost):
    '''
    Add otp user
    '''
    multihost.master.kinit_as_admin()
    # 1. Add IPA user
    add_ipa_user(multihost.master, multihost.testuser, multihost.password)
    multihost.master.kinit_as_user(multihost.testuser, multihost.password)


def mod_otp_user(multihost):
    '''
    Modify user
    '''
    #   log-in as admin
    multihost.master.kinit_as_admin()
    #   modify new user's authentication type
    multihost.master.qerun(['ipa',
                            'user-mod',
                            '--user-auth-type=otp',
                            multihost.testuser],
                           exp_returncode=0)


def add_otptoken(multihost):
    '''
    Add otptoken to new user
    '''
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
    print ("\n*****    OTPtoken added to new user successfully    *****\n")


def delete_otptoken(multihost):
    '''
    Deleting token
    '''
    multihost.master.qerun(['ipa',
                            'otptoken-del',
                            multihost.token],
                           exp_returncode=0,
                           exp_output='Deleted OTP token "%s"' % multihost.token)


def delete_otp_user(multihost):
    '''
    Kinit As admin and deleting user
    '''
    multihost.master.kinit_as_admin()
    multihost.master.qerun(['ipa',
                            'user-del',
                            multihost.testuser],
                           exp_returncode=0,
                           exp_output='Deleted user "%s"' % multihost.testuser)
