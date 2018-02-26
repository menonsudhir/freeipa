"""
OTP testcases
"""
from ipa_pytests.shared.utils import (kinit_as_user, get_base_dn)
from ipa_pytests.shared.user_utils import del_ipa_user
from .lib import (add_user, mod_otp_user, add_otptoken,
                  delete_otptoken)
from ipa_pytests.shared.rpm_utils import check_rpm
import pytest
import otp_lib as lib
import time


class TestOTPfunction(object):
    """ Test Class """

    def class_setup(self, multihost):
        """ Setup for class """
        multihost.realm = multihost.master.domain.realm

        # Common username and password for required testcases
        multihost.testuser = "mytestuser"
        multihost.token = "deftoken"
        REPOFILE = '/etc/yum.repos.d/repo-extra.repo'
        EXTRAREPO = "http://file.rdu.redhat.com/~spoore/idmqe-extras/7Server/x86_64/"
        new_repo_file = "[extra-repo]\n" + \
            "name=pavelextra\n" + \
            "baseurl=" + EXTRAREPO + "\n" + \
            "gpgcheck=0\n" + \
            "enabled=1\n"
        multihost.master.run_command(['touch', REPOFILE])
        multihost.master.transport.put_file_contents(
            REPOFILE, new_repo_file)
        check_rpm(multihost.master, ['oathtool'])


    def test_otp_0001(self, multihost):
        """
        IDM-IPA-TC: OTP: Add otptoken to new user and test with enabling FAST
        """
        multihost.testuser = 'testuser0001'
        multihost.nonotpuser = 'nonotpuser'

        # add otp user
        add_user(multihost)

        multihost.master.kinit_as_user(
            multihost.testuser, multihost.master.config.admin_pw)

        #   modify otp user as admin
        mod_otp_user(multihost)

        #   Add otptoken as admin
        multihost.master.kinit_as_admin()
        print("\nAdd token")
        token_key = lib.add_token(multihost, multihost.testuser)
        otp = lib.otp_key_convert(lib.get_otp_key(token_key))

        # krb auth with OTP
        krb_cache = lib.get_krb_cache(multihost, multihost.nonotpuser)
        krbotp = multihost.master.config.admin_pw + lib.get_otp(multihost, otp)
        time.sleep(3)
        print("kinit as %s with password + token : %s" % (multihost.testuser, krbotp))
        cmd = multihost.master.run_command([
              'kinit', '-T', krb_cache, multihost.testuser
               ], stdin_text=krbotp, raiseonerr=False)
        print cmd.stdout_text
        print cmd.stderr_text
        if cmd.returncode != 0:
            pytest.xfail("krb auth with otp failed")

        # Ldap bind with OTP

        time.sleep(60)
        base_dn = get_base_dn(multihost.master)
        print base_dn

        ldapotp = str(multihost.master.config.admin_pw + lib.get_otp(multihost, otp)).strip('\n')

        search = ['ldapsearch', '-xLLL',
                  '-D', 'uid='+multihost.testuser+',cn=users,cn=accounts,'+base_dn,
                  '-w', ldapotp,
                  '-h', multihost.master.hostname,
                  '-b', 'cn=users,cn=accounts,'+base_dn,
                  '-s', 'sub']

        cmd = multihost.master.run_command(search, raiseonerr=False)
        if cmd.returncode != 0:
            pytest.xfail("ldapauth with otp failed")
        print cmd.stdout_text
        print cmd.stderr_text
        #   delete otp user
        del_ipa_user(multihost.master, multihost.testuser)

    def test_otp_0002(self, multihost):
        """
       IDM-IPA-TC: OTP: Add otptoken to new user and test without enable FAST
         https://fedorahosted.org/freeipa/ticket/4411
        """
        multihost.testuser = 'otpuser0002'
        multihost.token = 'token0002'

        # add otp user
        add_user(multihost)

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
            exp_output='kinit: Pre-authentication failed: '
                       'Invalid argument while getting initial credentials')

        #   delete otp user
        del_ipa_user(multihost.master, multihost.testuser)

        #   delete otptoken
        delete_otptoken(multihost)

    def test_otp_0007(self, multihost):
        """
        IDM-IPA-TC: OTP: Log-in with Password only when authenticating type is OTP
        """
        multihost.testuser = 'otpuser0007'
        multihost.token = 'token0007'

        #   add otp user
        add_user(multihost)

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
        cmd = multihost.master.run_command(['kinit', '-T',
                                            'KEYRING:persistent:0:0',
                                            multihost.testuser],
                                           stdin_text=multihost.password,
                                           raiseonerr=False)
        exp_output = 'kinit: Preauthentication failed'
        if exp_output not in cmd.stderr_text:
            pytest.fail("Failed to verify")
        #   delete otp user
        del_ipa_user(multihost.master, multihost.testuser)

        #   delete otptoken
        delete_otptoken(multihost)

    def test_otp_0010(self, multihost):
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

    def test_otp_0013(self, multihost):
        """
        IDM-IPA-TC: OTP: Re-assign token to non-existing user(ipa otptoken-mod).
        """
        multihost.testuser = 'otpuser0013'
        multihost.token = 'token0013'
        multihost.xtrauser = 'otpuser0013a'

        #   add otp user
        add_user(multihost)

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
                                          ' user not found')

        #   delete otp user
        del_ipa_user(multihost.master, multihost.testuser)

        #   delete otptoken
        delete_otptoken(multihost)

    def test_otp_0015(self, multihost):
        """
        IDM-IPA-TC: OTP: Add multiple type of tokens for same user
        """
        multihost.testuser = 'otpuser0015'

        #   add otp user
        add_user(multihost)

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
        del_ipa_user(multihost.master, multihost.testuser)

    def test_otp_0020(self, multihost):
        """
        IDM-IPA-TC: OTP: Delete token
        """
        multihost.testuser = 'otpuser0020'

        #   add otp user
        add_user(multihost)

        #   Add otptoken as admin
        add_otptoken(multihost)

        #   delete otptoken
        delete_otptoken(multihost)
        print "\n*****   Token deleted successfully   *****\n"

        #   delete otp user
        del_ipa_user(multihost.master, multihost.testuser)

    def test_otp_0021(self, multihost):
        """
        IDM-IPA-TC: OTP: Find token as user
        """
        multihost.testuser = 'otpuser0021'
        multihost.token = 'token0021'

        #   add otp user
        add_user(multihost)

        #   Add otptoken as admin
        add_otptoken(multihost)

        #   kinit as user
        kinit_as_user(multihost.master, multihost.testuser, multihost.password)

        #   Find Token
        multihost.master.qerun(['ipa', 'otptoken-find'],
                               exp_returncode=0,
                               exp_output='Number of entries returned 1')

        #   delete otp user
        del_ipa_user(multihost.master, multihost.testuser)

    def test_otp_0022(self, multihost):
        """
        IDM-IPA-TC: OTP: Find token as admin
        """
        #   log-in as admin
        multihost.master.kinit_as_admin()

        #   Find Token
        multihost.master.qerun(['ipa', 'otptoken-find'],
                               exp_returncode=0,
                               exp_output='Number of entries returned')

    def test_otp_0023(self, multihost):
        """
        IDM-IPA-TC: OTP: Show token as user
        """
        multihost.testuser = 'otpuser0023'
        multihost.token = 'token0023'

        #   add otp user
        add_user(multihost)

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
        del_ipa_user(multihost.master, multihost.testuser)

    def test_otp_0024(self, multihost):
        """
        IDM-IPA-TC: OTP: Show token as admin
        """
        multihost.testuser = 'otpuser0024'
        multihost.token = 'token0024'

        #   add otp user
        add_user(multihost)

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
        del_ipa_user(multihost.master, multihost.testuser)

    def test_otp_0025(self, multihost):
        """
        IDM-IPA-TC: OTP: Assign invalid token type
        """
        multihost.testuser = 'otpuser0025'

        #   add otp user
        add_user(multihost)

        #   Add otptoken as admin
        multihost.master.qerun(['ipa', 'otptoken-add',
                                '--type=xyz', '--no-qrcode',
                                '--owner=%s' % multihost.testuser],
                               exp_returncode=1,
                               exp_output="ipa: ERROR: invalid 'type':")

        #   delete otp user
        del_ipa_user(multihost.master, multihost.testuser)

    def test_otp_0027(self, multihost):
        """
        IDM-IPA-TC: OTP: Add Same token ID to another user
        """
        multihost.testuser = 'otpuser0027'
        multihost.token = 'token0027'

        #   add otp user
        add_user(multihost)

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
        del_ipa_user(multihost.master, multihost.testuser)

        #   delete otptoken
        delete_otptoken(multihost)

    def test_otp_0034(self, multihost):
        """
        IDM-IPA-TC: OTP: Change authentication window to 2147483650 seconds_bz1200867
        """

        #   log-in as admin
        multihost.master.kinit_as_admin()

        # check otp configuration
        multihost.master.qerun(
            [
                'ipa',
                'otpconfig-show'],
            exp_returncode=0,
            exp_output='TOTP authentication Window: 300'
        )

        # change authentication window time to 2147483650 seconds
        multihost.master.qerun(['ipa',
                                'otpconfig-mod',
                                '--totp-auth-window=2147483650'],
                               exp_returncode=1,
                               exp_output='ipa: ERROR: invalid'
                               " 'totp_auth_window'"
                               ''
                               ': can be at most 2147483647')

    def test_otp_0035(self, multihost):
        """
        IDM-IPA-TC: OTP: Change authentication window to 0 seconds_bz1200867
        """

        #   log-in as admin
        multihost.master.kinit_as_admin()

        # check otp configuration
        multihost.master.qerun(
            [
                'ipa',
                'otpconfig-show'],
            exp_returncode=0,
            exp_output='TOTP authentication Window: 300'
        )

        # change authentication window time to 0 seconds
        multihost.master.qerun(['ipa',
                                'otpconfig-mod',
                                '--totp-auth-window=0'],
                               exp_returncode=1,
                               exp_output='ipa: ERROR: invalid'
                               " 'totp_auth_window'"
                               ''
                               ': must be at least 5')

    def test_otp_0036(self, multihost):
        """
        IDM-IPA-TC: OTP: Change authentication window to -5 seconds_bz1200867
        """

        #   log-in as admin
        multihost.master.kinit_as_admin()

        # check otp configuration
        multihost.master.qerun(
            [
                'ipa',
                'otpconfig-show'],
            exp_returncode=0,
            exp_output='TOTP authentication Window: 300'
        )

        # change authentication window time to -5 seconds
        multihost.master.qerun(['ipa',
                                'otpconfig-mod',
                                '--totp-auth-window=-5'],
                               exp_returncode=1,
                               exp_output='ipa: ERROR: invalid'
                               " 'totp_auth_window'"
                               ''
                               ': must be at least 5')

    def test_otp_0037(self, multihost):
        """
        IDM-IPA-TC: OTP: Change authentication window to non numaric value_bz1200867
        """

        #   log-in as admin
        multihost.master.kinit_as_admin()

        # check otp configuration
        multihost.master.qerun(
            [
                'ipa',
                'otpconfig-show'],
            exp_returncode=0,
            exp_output='TOTP authentication Window: 300'
        )

        # change authentication window time to @asd
        multihost.master.qerun(['ipa',
                                'otpconfig-mod',
                                '--totp-auth-window=@asd'],
                               exp_returncode=1,
                               exp_output='ipa: ERROR: invalid'
                               " 'totp_auth_window'"
                               ''
                               ': must be an integer')

    def test_otp_0038(self, multihost):
        """
        IDM-IPA-TC: OTP: Change authentication window with blank space_bz1200867
        """

        #   log-in as admin
        multihost.master.kinit_as_admin()

        # check otp configuration
        multihost.master.qerun(
            [
                'ipa',
                'otpconfig-show'],
            exp_returncode=0,
            exp_output='TOTP authentication Window: 300'
        )

        # change authentication window time with blank space
        multihost.master.qerun(['ipa',
                                'otpconfig-mod',
                                '--totp-auth-window='],
                               exp_returncode=1,
                               exp_output='ipa: ERROR:'
                               " 'totp_auth_window'"
                               ''
                               ' is required')

    def test_otp_0039(self, multihost):
        """
        IDM-IPA-TC: OTP: Change authentication window with leading space_bz1200867
        """

        #   log-in as admin
        multihost.master.kinit_as_admin()

        # check otp configuration
        multihost.master.qerun(
            [
                'ipa',
                'otpconfig-show'],
            exp_returncode=0,
            exp_output='TOTP authentication Window: 300'
        )

        # change authentication window time with leading space
        multihost.master.qerun(['ipa',
                                'otpconfig-mod',
                                '--totp-auth-window=', ' 123'],
                               exp_returncode=1,
                               exp_output='ipa: ERROR:'
                               " command 'otpconfig_mod'"
                               ''
                               ' takes no argument')

    def test_otp_0042(self, multihost):
        """
        IDM-IPA-TC: OTP: Change synchronization window to 2147483650 seconds_bz1200867
        """

        #   log-in as admin
        multihost.master.kinit_as_admin()

        # check otp configuration
        multihost.master.qerun(
            [
                'ipa',
                'otpconfig-show'],
            exp_returncode=0,
            exp_output='TOTP Synchronization Window: 86400'
        )

        # change synchronization window time to 2147483650 seconds
        multihost.master.qerun(['ipa',
                                'otpconfig-mod',
                                '--totp-sync-window=2147483650'],
                               exp_returncode=1,
                               exp_output='ipa: ERROR: invalid'
                               " 'totp_sync_window'"
                               ''
                               ': can be at most 2147483647')

    def test_otp_0043(self, multihost):
        """
        IDM-IPA-TC: OTP: Change synchronization window to 0 seconds_bz1200867
        """

        #   log-in as admin
        multihost.master.kinit_as_admin()

        # check otp configuration
        multihost.master.qerun(
            [
                'ipa',
                'otpconfig-show'],
            exp_returncode=0,
            exp_output='TOTP Synchronization Window: 86400'
        )

        # change synchronization window time to 0 seconds
        multihost.master.qerun(['ipa',
                                'otpconfig-mod',
                                '--totp-sync-window=0'],
                               exp_returncode=1,
                               exp_output='ipa: ERROR: invalid'
                               " 'totp_sync_window'"
                               ''
                               ': must be at least 5')

    def test_otp_0044(self, multihost):
        """
        IDM-IPA-TC: OTP: Change synchronization window to -5 seconds_bz1200867
        """

        #   log-in as admin
        multihost.master.kinit_as_admin()

        # check otp configuration
        multihost.master.qerun(
            [
                'ipa',
                'otpconfig-show'],
            exp_returncode=0,
            exp_output='TOTP Synchronization Window: 86400'
        )

        # change synchronization window time to -5 seconds
        multihost.master.qerun(['ipa',
                                'otpconfig-mod',
                                '--totp-sync-window=-5'],
                               exp_returncode=1,
                               exp_output='ipa: ERROR: invalid'
                               " 'totp_sync_window'"
                               ''
                               ': must be at least 5')

    def test_otp_0045(self, multihost):
        """
        IDM-IPA-TC: OTP: Change synchronization window to non numaric value_bz1200867
        """

        #   log-in as admin
        multihost.master.kinit_as_admin()

        # check otp configuration
        multihost.master.qerun(
            [
                'ipa',
                'otpconfig-show'],
            exp_returncode=0,
            exp_output='TOTP Synchronization Window: 86400'
        )

        # change synchronization window time to @asd
        multihost.master.qerun(['ipa',
                                'otpconfig-mod',
                                '--totp-sync-window=@asd'],
                               exp_returncode=1,
                               exp_output='ipa: ERROR: invalid'
                               " 'totp_sync_window'"
                               ''
                               ': must be an integer')

    def test_otp_0046(self, multihost):
        """
        IDM-IPA-TC: OTP: Change synchronization window with blank space_bz1200867
        """

        #   log-in as admin
        multihost.master.kinit_as_admin()

        # check otp configuration
        multihost.master.qerun(
            [
                'ipa',
                'otpconfig-show'],
            exp_returncode=0,
            exp_output='TOTP Synchronization Window: 86400'
        )

        # change synchronization window time with blank space
        multihost.master.qerun(['ipa',
                                'otpconfig-mod',
                                '--totp-sync-window='],
                               exp_returncode=1,
                               exp_output='ipa: ERROR:'
                               " 'totp_sync_window'"
                               ''
                               ' is required')

    def test_otp_0047(self, multihost):
        """
        IDM-IPA-TC: OTP: Change synchronization window with leading space_bz1200867
        """

        #   log-in as admin
        multihost.master.kinit_as_admin()

        # check otp configuration
        multihost.master.qerun(
            [
                'ipa',
                'otpconfig-show'],
            exp_returncode=0,
            exp_output='TOTP Synchronization Window: 86400'
        )

        # change synchronization window time with leading space
        multihost.master.qerun(['ipa',
                                'otpconfig-mod',
                                '--totp-sync-window=', ' 123'],
                               exp_returncode=1,
                               exp_output='ipa: ERROR:'
                               " command 'otpconfig_mod'"
                               ''
                               ' takes no argument')

    def class_teardown(self, multihost):
        """ Teardown for class """
        pass
