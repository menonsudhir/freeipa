""" Authentication Indicators Test Suite """
from ipa_pytests.otp import otp_lib as lib
from ipa_pytests.shared.user_utils import mod_ipa_user
from ipa_pytests.shared.service_utils import service_mod, service_show
from ipa_pytests.shared.host_utils import host_mod
import time

TUSER = 'tuser01'
TESTUSER = 'tuser02'
INFOUSER = 'info'
RADUSER = 'raduser01'
RADPASS = 'testing123'
SERVICENAME = ''
OTP = ''
OTP2 = ''
NEW_HOST = ''


class TestAuthIndent(object):
    """ Authentication Identification test """

    def test000(self, multihost):
        """Setup"""
        multihost.master.kinit_as_admin()
        global SERVICENAME
        SERVICENAME = "%s/%s@%s" % (
            'DNS', multihost.master.hostname,
            multihost.master.domain.realm)
        global NEW_HOST
        NEW_HOST = 'another01.' + multihost.master.domain.realm
        lib.add_user(multihost, TUSER)

    def test001(self, multihost):
        """
        @Title: IDM-IPA-TC: Authentication Indicators: Add another authentication indicators for existing service
        @casecomponent: ipa
        """
        print('\nServicename global : ')
        print(SERVICENAME)
        multihost.master.kinit_as_admin()
        print("%s mod" % SERVICENAME)
        service_mod(multihost.master, SERVICENAME, {'auth-ind': 'otp'})
        print("%s mod done" % SERVICENAME)
        cmd = service_show(multihost.master, SERVICENAME)
        assert "otp" in cmd.stdout_text
        print(SERVICENAME + " mod")
        cmd1 = service_mod(
            multihost.master,
            SERVICENAME,
            {'auth-ind': ['otp', 'radius']})
        print("mod 2 done")
        assert any(x in cmd1.stdout_text for x in ("otp", "radius"))

    def test002(self, multihost):
        """
        @Title: IDM-IPA-TC: Authentication Indicators: Access service only with sufficient otp authentication
        @casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        print("\nAdd token")
        token_key = lib.add_token(multihost, TUSER)
        global OTP
        OTP = lib.otp_key_convert(lib.get_otp_key(token_key))
        service_mod(multihost.master, SERVICENAME, {'auth-ind': 'otp'})
        mod_ipa_user(
            multihost.master, TUSER,
            ['--user-auth-type=otp',
             '--user-auth-type=password',
             '--user-auth-type=radius'])
        multihost.master.kinit_as_user(
            TUSER, multihost.master.config.admin_pw)
        multihost.master.qerun([
            'kvno', SERVICENAME
            ], exp_returncode=1)
        krb_cache = lib.get_krb_cache(multihost, INFOUSER)
        password = multihost.master.config.admin_pw + lib.get_otp(multihost, OTP)
        time.sleep(3)
        print("kinit as %s with password + token : %s" % (TUSER, password))
        multihost.master.run_command([
            'kinit', '-T', krb_cache, TUSER
            ], stdin_text=password)
        multihost.master.run_command([
            'kvno', SERVICENAME])
        multihost.master.kinit_as_admin()
        service_mod(
            multihost.master,
            SERVICENAME,
            {'auth-ind': ['otp', 'radius', 'password']})

    def test003(self, multihost):
        """
        @Title: IDM-IPA-TC: Authentication Indicators: Add multiple authentication indicator for service and try to access with different authentication types users(otpuser and radiususer)
        @casecomponent: ipa
        """
        print("\nAdd radius user and setup server")
        multihost.master.run_command([
            'yum', 'remove', 'freeradius', 'freeradius-ldap',
            'freeradius-utils', '-y'])
        multihost.master.run_command([
            'yum', 'install', 'freeradius', 'freeradius-ldap',
            'freeradius-utils', '-y'])
        lib.prepare_radiusd(multihost, RADUSER)
        lib.add_user(multihost, RADUSER)
        radpassword = "%s\n%s" % (RADPASS, RADPASS)
        multihost.master.kinit_as_admin()
        multihost.master.run_command([
            'ipa', 'radiusproxy-add', 'testproxy01', '--server=127.0.0.1'
            ], stdin_text=radpassword)
        mod_ipa_user(
            multihost.master, RADUSER,
            ['--radius=testproxy01',
             '--user-auth-type=radius'])
        service_mod(multihost.master, SERVICENAME, {'auth-ind': 'radius'})
        password = multihost.master.config.admin_pw
        krb_cache = lib.get_krb_cache(multihost, INFOUSER)
        multihost.master.run_command([
            'kinit', '-T', krb_cache, RADUSER
            ], stdin_text=password)
        multihost.master.run_command([
            'kvno', SERVICENAME])
        multihost.master.kinit_as_admin()
        service_mod(
            multihost.master,
            SERVICENAME,
            {'auth-ind': ['otp', 'radius']})
        password = multihost.master.config.admin_pw + lib.get_otp(multihost, OTP)
        time.sleep(3)
        krb_cache = lib.get_krb_cache(multihost, INFOUSER)
        multihost.master.run_command([
            'kinit', '-T', krb_cache, TUSER
            ], stdin_text=password)
        multihost.master.run_command([
            'kvno', SERVICENAME])

    def test004(self, multihost):
        """
        @Title: IDM-IPA-TC: Authentication Indicators: Add new authentication indicator for service and try to access with OTP and Radius authentication types users
        @casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        service_mod(multihost.master, SERVICENAME, {'auth-ind': 'otp'})
        password = multihost.master.config.admin_pw
        krb_cache = lib.get_krb_cache(multihost, INFOUSER)
        multihost.master.run_command([
            'kinit', '-T', krb_cache, RADUSER
            ], stdin_text=password)
        multihost.master.qerun([
            'kvno', SERVICENAME
            ], exp_returncode=1)
        krb_cache = lib.get_krb_cache(multihost, INFOUSER)
        time.sleep(3)
        password = multihost.master.config.admin_pw + lib.get_otp(multihost, OTP)
        time.sleep(3)
        multihost.master.run_command([
            'kinit', '-T', krb_cache, TUSER
            ], stdin_text=password)
        time.sleep(10)
        multihost.master.run_command([
            'kvno', SERVICENAME])

    def test005(self, multihost):
        """
        @Title: IDM-IPA-TC: Authentication Indicators: Add authentication indicator with leading space
        @casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        cmd = mod_ipa_user(
            multihost.master, TUSER,
            ['--user-auth-type= otp'], raiseonerr=False)
        assert cmd.returncode == 1

    def test006(self, multihost):
        """
        @Title: IDM-IPA-TC: Authentication Indicators: Add authentication indicator with trailing space
        @casecomponent: ipa
        """
        cmd = mod_ipa_user(
            multihost.master, TUSER,
            ['--user-auth-type=otp '], raiseonerr=False)
        assert cmd.returncode == 1

    def test007(self, multihost):
        """
        @Title: IDM-IPA-TC: Authentication Indicators: Add authentication indicator with capital letters (eg: OTP, RADIUS)
        @casecomponent: ipa
        """
        cmd = mod_ipa_user(
            multihost.master, TUSER,
            ['--user-auth-type=OTP'], raiseonerr=False)
        assert cmd.returncode == 1
        cmd = mod_ipa_user(
            multihost.master, TUSER,
            ['--user-auth-type=RADIUS'], raiseonerr=False)
        assert cmd.returncode == 1

    def test008(self, multihost):
        """
        @Title: IDM-IPA-TC: Authentication Indicators: Try to access host with sufficient authentication
        @casecomponent: ipa
        """
        host_mod(
            multihost.master,
            multihost.master.hostname,
            {'auth-ind': 'radius'})
        password = multihost.master.config.admin_pw
        krb_cache = lib.get_krb_cache(multihost, INFOUSER)
        multihost.master.run_command([
            'kinit', '-T', krb_cache, RADUSER
            ], stdin_text=password)
        krb_cache = lib.get_krb_cache(multihost, INFOUSER, multihost.client)
        multihost.client.run_command([
            'kinit', '-T', krb_cache, RADUSER
            ], stdin_text=password)
        lib.ssh_test(multihost, RADUSER)

    def test009(self, multihost):
        """
        @Title: IDM-IPA-TC: Authentication Indicators: Create new host entry with specified authentication indicator
        @casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command([
            'ipa', 'host-add',
            '--auth-ind=otp',
            '--force', NEW_HOST
            ])
        assert "otp" in cmd.stdout_text

    def test010(self, multihost):
        """
        @Title: IDM-IPA-TC: Authentication Indicators: Update existing host entry to another authentication indicator
        @casecomponent: ipa
        """
        cmd = host_mod(multihost.master, NEW_HOST, {'auth-ind': 'radius'})
        assert "radius" in cmd.stdout_text

    def test011(self, multihost):
        """
        @Title: IDM-IPA-TC: Authentication Indicators: Verify that both authentication indicators can be set for a host
        @casecomponent: ipa
        """
        cmd = host_mod(
            multihost.master,
            NEW_HOST,
            {'auth-ind': ['radius', 'otp']})
        assert all(x in cmd.stdout_text for x in ("otp", "radius"))

    def test012(self, multihost):
        """
        @Title: IDM-IPA-TC: Authentication Indicators: Remove authentication indicators from hosts
        @casecomponent: ipa
        """
        cmd = host_mod(
            multihost.master,
            NEW_HOST,
            {'auth-ind': '""'})
        assert not any(x in cmd.stdout_text for x in ("otp", "radius"))

    def test013(self, multihost):
        """
        @Title: IDM-IPA-TC: Authentication Indicators: Access hosts without authentication indicators
        @casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        multihost.client.kinit_as_admin()
        lib.add_user(multihost, TESTUSER)
        token_key = lib.add_token(multihost, TESTUSER)
        print(token_key)
        global OTP2
        OTP2 = lib.otp_key_convert(lib.get_otp_key(token_key))
        print(OTP2)
        print(lib.get_otp(multihost, OTP2))
        mod_ipa_user(
            multihost.master, TESTUSER,
            ['--user-auth-type=otp',
             '--user-auth-type=password',
             '--user-auth-type=radius'])
        host_mod(
            multihost.master,
            multihost.master.hostname,
            {'auth-ind=':''})
        multihost.master.run_command([
            'ipa', 'user-unlock', TESTUSER])
        multihost.master.run_command([
            'sss_cache', '-E'])
        multihost.master.run_command([
            'ipactl', 'restart'])
        time.sleep(13)
        multihost.client.kinit_as_user(
            TESTUSER, multihost.master.config.admin_pw)
        multihost.client.run_command(['klist'])
        time.sleep(5)
        lib.ssh_test(multihost, TESTUSER)
        krb_cache = lib.get_krb_cache(multihost, INFOUSER, multihost.client)
        password = multihost.master.config.admin_pw + lib.get_otp(
            multihost, OTP2)
        time.sleep(3)
        cmd = multihost.client.run_command([
            'kinit', '-T', krb_cache, TESTUSER
            ], stdin_text=password, raiseonerr=False)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        time.sleep(5)
        lib.ssh_test(multihost, TESTUSER)

    def test014(self, multihost):
        """
        @Title: IDM-IPA-TC: Authentication Indicators: Try to access host with insufficient authentication
        @casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        host_mod(
            multihost.master,
            multihost.master.hostname,
            {'auth-ind': 'otp'})
        multihost.client.kinit_as_user(
            TESTUSER, multihost.master.config.admin_pw)
        lib.ssh_neg_test(multihost, TESTUSER)
        lib.krb_destroy(multihost.client)
        krb_cache = lib.get_krb_cache(multihost, INFOUSER, multihost.client)
        time.sleep(3)
        password = multihost.master.config.admin_pw + lib.get_otp(
            multihost, OTP2)
        time.sleep(3)
        multihost.client.run_command([
            'kinit', '-T', krb_cache, TESTUSER
            ], stdin_text=password)
        time.sleep(10)
        lib.ssh_test(multihost, TESTUSER)

    def test015(self, multihost):
        """
        @Title: IDM-IPA-TC: Authentication Indicators: Add authentication indicator with special characters
        @casecomponent: ipa
        """
        service_mod(multihost.master, SERVICENAME, {'auth-ind': '%@!#'})

    def test016(self, multihost):
        """
        @Title: IDM-IPA-TC: Authentication Indicators: Modify existing service entry to different authentication indicator as user
        @casecomponent: ipa
        """
        multihost.master.kinit_as_user(
            INFOUSER,
            multihost.master.config.admin_pw)
        cmd = service_mod(
            multihost.master,
            SERVICENAME,
            {'auth-ind': 'otp'},
            raiseonerr=False)
        assert cmd.returncode == 1
