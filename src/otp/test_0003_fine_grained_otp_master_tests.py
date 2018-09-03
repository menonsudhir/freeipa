"""
Fine-grained OTP authentication testcases
"""
from ipa_pytests.shared.user_utils import del_ipa_user
from ipa_pytests.otp.lib import (add_user, add_otptoken,
                                 delete_otptoken)


class TestFineGrainedOTP(object):
    """ Test Class """

    def test_second_factor_optional(self, multihost):
        """
        IDM-IPA-TC: OTP: Verifying OTP/2FA authentication optional while login BZ=1325809
        """
        multihost.testuser = 'otpuser1325809'
        multihost.token = "deftoken"
        exp_output1 = 'User authentication types: otp, password'

        # add user
        add_user(multihost)

        #   modify user as admin
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa',
                                'user-mod',
                                '--user-auth-type=otp',
                                '--user-auth-type=password',
                                multihost.testuser],
                               exp_returncode=0)

        # Verifying user's authentication types
        multihost.master.qerun(['ipa',
                                'user-show',
                                '%s' % multihost.testuser],
                               exp_returncode=0,
                               exp_output=exp_output1)

        #   Add otptoken as admin
        add_otptoken(multihost)

        # ssh as user: to verify 2FA authentication is optional while login
        expect_script = 'set timeout 15\n'
        expect_script = 'spawn ssh -l ' + multihost.testuser + \
                        ' '+ multihost.master.hostname + '\n'
        expect_script += 'expect "Are you sure you want to continue connecting (yes/no)?"\n'
        expect_script += 'send "yes\r"\n'
        expect_script += 'expect "First Factor:"\n'
        expect_script += 'send "'+ multihost.password + '\r"\n'
        expect_script += 'expect "Second Factor (optional):"\n'
        expect_script += 'send "\r"\n'
        expect_script += 'expect "$"\n'
        expect_script += 'send "id\r"\n'
        expect_script += 'expect "uid=*"\n'
        expect_script += 'send "su ' +multihost.testuser +'\r"\n'
        expect_script += 'expect "First Factor:"\n'
        expect_script += 'send "' + multihost.password + '\r"\n'
        expect_script += 'expect "Second Factor (optional):"\n'
        expect_script += 'expect EOF\n'
        output = multihost.master.expect(expect_script)
        print("\n Credentials are promoted successfully" \
                " from 1FA to 2FA by calling 'su' ")

        #   delete otptoken
        delete_otptoken(multihost)
        print("\n*****   Token deleted successfully   *****\n")

        #   delete user
        del_ipa_user(multihost.master, multihost.testuser)
