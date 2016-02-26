"""
OTP testcases
"""

from ipa_pytests.shared.utils import (kinit_as_user)
from .lib import (add_otp_user, mod_otp_user, add_otptoken,
                  delete_otptoken, delete_otp_user)


class TestOTPfunction(object):
    """ Test Class """

    def class_setup(self, multihost):
        """ Setup for class """
        multihost.realm = multihost.master.domain.realm

        # Common username and password for required testcases
        multihost.testuser = "mytestuser"
        multihost.password = "Secret123"
        chpass = "Passw0rd1"
        multihost.token = "deftoken"
        multihost.chpasswd = "%s\n%s\n%s\n" % (multihost.password,
                                               chpass,
                                               chpass)
        multihost.repasswd = "%s\n%s\n%s\n" % (chpass,
                                               multihost.password,
                                               multihost.password)

    def test_0002_without_enable_fast(self, multihost):
        """
       IDM-IPA-TC: OTP: Add otptoken to new user and test without enable FAST
         https://fedorahosted.org/freeipa/ticket/4411
        """
        multihost.testuser = 'otpuser0002'
        multihost.token = 'token0002'

        # add otp user
        add_otp_user(multihost)

        #   modify otp user as admin
        mod_otp_user(multihost)

        #   Add otptoken as admin
        add_otptoken(multihost)

        # Log in as OTP user without manually enabled FAST
        multihost.master.qerun(
            [
                'kinit',
                '{}'.format(
                    multihost.testuser)],
            exp_returncode=1,
            exp_output='kinit: Generic preauthentication')

        #   delete otp user
        delete_otp_user(multihost)

        #   delete otptoken
        delete_otptoken(multihost)

    def test_0007_otp_login_with_onlypassword(self, multihost):
        """
        IDM-IPA-TC: OTP: Log-in with Password only when authenticating type is OTP
        """
        multihost.testuser = 'otpuser0007'
        multihost.token = 'token0007'

        #   add otp user
        add_otp_user(multihost)

        #   modify otp user as admin
        mod_otp_user(multihost)

        #   Add otptoken as admin
        add_otptoken(multihost)

        #   Log in as OTP user with manually
        # enabled FAST and enter only password
        multihost.master.qerun(['kdestroy', '-A'], exp_returncode=0)
        multihost.master.qerun(['kswitch', '-c', 'KEYRING:persistent:0:0'],
                               exp_returncode=0)
        multihost.master.kinit_as_admin()
        multihost.master.qerun(
            [
                'kinit',
                '-T',
                'KEYRING:persistent:0:0',
                '{}'.format(
                    multihost.testuser)],
            stdin_text=multihost.password,
            exp_returncode=1,
            exp_output='kinit: Preauthentication failed')

        #   delete otp user
        delete_otp_user(multihost)

        #   delete otptoken
        delete_otptoken(multihost)

    def test_0010_otp_assign_new_token_to_nonexisting_user(self, multihost):
        """
        IDM-IPA-TC: OTP: Assign token to non-existing user
        """

        multihost.testuser = 'otpuser0010'

        #   Add otptoken to non existing user as admin
        multihost.master.qerun(['ipa', 'otptoken-add', '--type=totp',
                                '--no-qrcode',
                                '--owner={}'.format(multihost.testuser)],
                               exp_returncode=2,
                               exp_output='ipa: ERROR: otpuser0010: '
                                          'user not found')

    def test_0013_otp_reassign_token_to_nonexisting_user(self, multihost):
        """
        IDM-IPA-TC: OTP: Re-assign token to non-existing user(ipa otptoken-mod).
        """
        multihost.testuser = 'otpuser0013'
        multihost.token = 'token0013'
        multihost.xtrauser = 'otpuser0013a'

        #   add otp user
        add_otp_user(multihost)

        #   modify otp user as admin
        mod_otp_user(multihost)

        #   Add otptoken as admin
        add_otptoken(multihost)

        #   re-assign token to non-existing user
        multihost.master.qerun(['ipa', 'otptoken-mod',
                                '--owner=%s' % multihost.xtrauser,
                                '%s' % multihost.token],
                               exp_returncode=2,
                               exp_output='ipa: ERROR: otpuser0013a:'
                                          'user not found')

        #   delete otp user
        delete_otp_user(multihost)

        #   delete otptoken
        delete_otptoken(multihost)

    def test_0015_otp_add_multiple_type_of_token(self, multihost):
        """
        IDM-IPA-TC: OTP: Add multiple type of tokens for same user
        """
        multihost.testuser = 'otpuser0015'

        #   add otp user
        add_otp_user(multihost)

        #   modify otp user as admin
        mod_otp_user(multihost)

        #   Add TOTP token as admin
        multihost.master.qerun(['ipa', 'otptoken-add',
                                '--type=totp', '--no-qrcode',
                                '--owner=%s' % multihost.testuser],
                               exp_returncode=0,
                               exp_output='Type: TOTP')
        print "\n***** TOTP token added successfully *****\n"

        #   Add HOTP token as admin
        multihost.master.qerun(['ipa', 'otptoken-add',
                                '--type=hotp', '--no-qrcode',
                                '--owner=%s' % multihost.testuser],
                               exp_returncode=0, exp_output='Type: HOTP')
        print "\n*****    HOTP token also added successfully    *****\n"

        #   delete otp user
        delete_otp_user(multihost)

    def test_0020_otp_delete_token(self, multihost):
        """
        IDM-IPA-TC: OTP: Delete token
        """
        multihost.testuser = 'otpuser0020'

        #   add otp user
        add_otp_user(multihost)

        #   Add otptoken as admin
        add_otptoken(multihost)

        #   delete otptoken
        delete_otptoken(multihost)
        print "\n*****   Token deleted successfully   *****\n"

        #   delete otp user
        delete_otp_user(multihost)

    def test_0021_otp_find_token_as_user(self, multihost):
        """
        IDM-IPA-TC: OTP: Find token as user
        """
        multihost.testuser = 'otpuser0021'
        multihost.token = 'token0021'

        #   add otp user
        add_otp_user(multihost)

        #   Add otptoken as admin
        add_otptoken(multihost)

        #   kinit as user
        kinit_as_user(multihost.master, multihost.testuser, multihost.password)

        #   Find Token
        multihost.master.qerun(['ipa', 'otptoken-find'],
                               exp_returncode=0,
                               exp_output='Number of entries returned 1')

        #   delete otp user
        delete_otp_user(multihost)

    def test_0022_otp_find_token_as_admin(self, multihost):
        """
        IDM-IPA-TC: OTP: Find token as admin
        """
        #   log-in as admin
        multihost.master.kinit_as_admin()

        #   Find Token
        multihost.master.qerun(['ipa', 'otptoken-find'],
                               exp_returncode=0,
                               exp_output='Number of entries returned')

    def test_0023_otp_show_token_as_user(self, multihost):
        """
        IDM-IPA-TC: OTP: Show token as user
        """
        multihost.testuser = 'otpuser0023'
        multihost.token = 'token0023'

        #   add otp user
        add_otp_user(multihost)

        #   Add otptoken as admin
        add_otptoken(multihost)

        #   kinit as user
        kinit_as_user(multihost.master, multihost.testuser, multihost.password)

        #   show Token
        multihost.master.qerun(['ipa', 'otptoken-show',
                                multihost.token],
                               exp_returncode=0,
                               exp_output='Unique ID: %s' % multihost.token)

        #   delete otp user
        delete_otp_user(multihost)

    def test_0024_otp_show_token_as_admin(self, multihost):
        """
        IDM-IPA-TC: OTP: Show token as admin
        """
        multihost.testuser = 'otpuser0024'
        multihost.token = 'token0024'

        #   add otp user
        add_otp_user(multihost)

        #   Add otptoken as admin
        add_otptoken(multihost)

        #   kinit as admin
        multihost.master.kinit_as_admin()

        #   show Token
        multihost.master.qerun(['ipa',
                                'otptoken-show',
                                multihost.token],
                               exp_returncode=0,
                               exp_output='Unique ID: %s' % multihost.token)

        #   delete otp user
        delete_otp_user(multihost)

    def test_0025_otp_assign_invalid_token_type(self, multihost):
        """
        IDM-IPA-TC: OTP: Assign invalid token type
        """
        multihost.testuser = 'otpuser0025'

        #   add otp user
        add_otp_user(multihost)

        #   Add otptoken as admin
        multihost.master.qerun(['ipa', 'otptoken-add',
                                '--type=xyz', '--no-qrcode',
                                '--owner=%s' % multihost.testuser],
                               exp_returncode=1,
                               exp_output="ipa: ERROR: invalid 'type':")

        #   delete otp user
        delete_otp_user(multihost)

    def test_0027_otp_add_same_token_id_to_another_user(self, multihost):
        """
        IDM-IPA-TC: OTP: Add Same token ID to another user
        """
        multihost.testuser = 'otpuser0027'
        multihost.token = 'token0027'

        #   add otp user
        add_otp_user(multihost)

        # kinit as admin
        multihost.master.kinit_as_admin()

        #   Add otptoken as admin
        add_otptoken(multihost)

        #   Add same token to another user
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
            exp_returncode=1,
            exp_output='ipa: ERROR: OTP token with name "%s" already exists' %
            multihost.token)

        #   delete otp user
        delete_otp_user(multihost)

        #   delete otptoken
        delete_otptoken(multihost)

    def class_teardown(self, multihost):
        """ Teardown for class """
        pass
