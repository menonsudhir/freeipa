"""
More bug checks for server install
This can include any variety of test cases
"""

import re
import time
import pytest
from ipa_pytests.qe_install import setup_master, uninstall_server
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.utils import ipa_config_mod
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.shared.utils import ldapmodify_cmd, service_control
from ipa_pytests.qe_class import qe_use_class_setup


class TestBugChecks2(object):
    """ More bug checks for server install """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("OTHER : %s" % multihost.others[0].hostname)
        print("*" * 80)
        setup_master(multihost.master)
        setup_master(multihost.others[0])

    def test_0001_bz1205264(self, multihost):
        """
        Testcase to verify bz1205264
        TestCase related to IPA Migration DS
        """
        master1 = multihost.master
        other1 = multihost.others[0]

        master1.kinit_as_admin()
        other1.kinit_as_admin()
        # Create user
        user_range = 1
        user_ext = "testuser_"
        password = "Secret123"
        seconds = 20

        print("Creating test IPA user")
        for i in range(user_range):
            user = user_ext + str(i)
            print("Creating IPA user [%s]" % user)
            add_ipa_user(other1, user, password)

        # Modify ldap to allow anonymous access
        ldif_data = "dn: cn=config\n" \
                    "changetype: modify\n" \
                    "replace: nsslapd-allow-anonymous-access\n" \
                    "nsslapd-allow-anonymous-access: %s\n"
        for status in ['on', 'off']:
            ldif_file = '/tmp/ldap_annoymous_{}.ldif'.format(status)
            master1.put_file_contents(ldif_file, ldif_data % status)

        # Allow annonymous access
        status = 'off'
        ldif_off_file = '/tmp/ldap_annoymous_{}.ldif'.format(status)
        uri = 'ldap://' + other1.hostname + ':389'
        username = 'cn=Directory Manager'
        ldapmodify_cmd(master1, uri, username, password, ldif_off_file)

        # Enable migration on master server
        print("Enabling IPA migration on %s server" % master1.hostname)
        cmd = ipa_config_mod(multihost, opts=['--enable-migration=true'])
        if cmd in [0, 1]:
            print("IPA is already enabled with migration")
        else:
            pytest.fail("Unable to enable IPA migration on IPA server")

        # Disable IPA compat manage plugin
        print("Disabling IPA compat manage plugin "
              "on %s server" % master1.hostname)
        cmd = master1.run_command(['ipa-compat-manage', 'disable'],
                                  stdin_text=password,
                                  raiseonerr=False)
        if cmd.returncode == 2:
            print("IPA compat manage plugin is already disabled")
        elif cmd.returncode == 0:
            print("Disabled IPA compat manage plugin")
        else:
            pytest.fail("Failed to disable IPA compat manage plugin")

        # Restart dirsrv
        print("Restarting dirsrv on server [%s]" % master1.hostname)
        realm = master1.domain.realm.upper().replace('.', '-')
        service_control(master1, 'dirsrv@' + realm, 'restart')

        print("Sleeping for [%d] seconds" % seconds)
        time.sleep(seconds)

        # Migrating users
        print("Starting migration ...")
        cmdstr = ['ipa', 'migrate-ds',
                  '--user-container=cn=users,cn=accounts',
                  '--group-container=cn=groups,cn=accounts',
                  '--group-objectclass=posixgroup',
                  '--user-ignore-attribute={krbPrincipalName,krbextradata,'
                  'krblastfailedauth,'
                  'krblastpwdchange,krblastsuccessfulauth,krbloginfailedcount,'
                  'krbpasswordexpiration,'
                  'krbticketflags,krbpwdpolicyreference,mepManagedEntry}',
                  '--user-ignore-objectclass=mepOriginEntry',
                  '--with-compat',
                  'ldap://' + other1.hostname]
        cmdstr = " ".join(cmdstr)
        cmd = master1.run_command(cmdstr,
                                  stdin_text=password,
                                  raiseonerr=False)
        if cmd.returncode != 0:
            print(cmd.stdout_text, cmd.stderr_text)
            pytest.fail("Failed to run IPA migrate ds "
                        "command [%s]" % cmdstr)
        else:
            err = False
            for i in range(user_range):
                user = user_ext + str(i)
                if user not in cmd.stdout_text:
                    err = True
            if err:
                pytest.fail("Failed to verify BZ#1205264")

        # Cleanup
        master1.kinit_as_admin()
        other1.kinit_as_admin()

        cmd = master1.run_command(['ipa-compat-manage', 'enable'],
                                  stdin_text=password,
                                  raiseonerr=False)
        if cmd.returncode != 0:
            pytest.fail("Failed to enable IPA compat manage plugin")

        print("Restarting dirsrv on server [%s]" % master1.hostname)
        service_control(master1, 'dirsrv@' + realm, 'restart')

        cmd = ipa_config_mod(multihost, opts=['--enable-migration=false'])
        if cmd in [0, 1]:
            print("IPA is already disabled with migration")
        else:
            pytest.fail("Unable to disable IPA migration on IPA server")

        # Cleanup
        print("Deleting test IPA users")
        for i in range(user_range):
            user = user_ext + str(i)
            print("Deleting IPA user [%s]" % user)
            other1.run_command('ipa user-del %s' % user, raiseonerr=False)
            master1.run_command('ipa user-del %s' % user, raiseonerr=False)

        status = 'on'
        ldif_on_file = '/tmp/ldap_annoymous_{}.ldif'.format(status)
        uri = 'ldap://' + other1.hostname + ':389'
        username = 'cn=Directory Manager'
        ldapmodify_cmd(master1, uri, username, password, ldif_on_file)

    def test_0002_bz1319912(self, multihost):
        """
        IDM-IPA-TC: server-install: installer changes hostname
        This is to verify fix from bz1319912
        """
        master = multihost.master
        # uninstall master to start clean
        uninstall_server(master)
        # backup /etc/hosts
        etc_hosts = master.get_file_contents('/etc/hosts')
        master.put_file_contents('/etc/hosts.bz1319912.backup', etc_hosts)
        # create clean /etc/hosts with localhost and master only
        found = re.search('(?P<localhost>127.*localhost.*\n::1.*localhost.*\n)',
                          etc_hosts, re.MULTILINE)
        etc_hosts = found.group('localhost')
        etc_hosts += '{} {}'.format(master.ip, master.hostname)
        master.put_file_contents('/etc/hosts', etc_hosts)
        # backup /etc/hostname
        etc_hostname = master.get_file_contents('/etc/hostname')
        master.put_file_contents('/etc/hostname.bz1319912.backup', etc_hostname)
        # create clean /etc/hostname with different name
        if master.external_hostname is master.hostname:
            tmp_name = "bz1319912.fakedomain.test"
        else:
            tmp_name = master.external_hostname
        master.put_file_contents('/etc/hostname', tmp_name)
        master.qerun('hostnamectl')
        # run ipa-server-install with hostname/ip specified
        master.qerun(['ipa-server-install', '-U',
                      '--setup-dns',
                      '--forwarder', master.config.dns_forwarder,
                      '--domain', master.domain.name,
                      '--realm', master.domain.realm,
                      '--hostname', master.hostname,
                      '--ip-address', master.ip,
                      '--admin-password', master.config.admin_pw,
                      '--ds-password', master.config.dirman_pw])
        # make sure no error in log.
        # grep used instead of get_file_contents due to size of file
        master.qerun(['grep', r'ERROR.*named-pkcs11',
                      '/var/log/ipaserver-install.log'],
                     exp_returncode=1)
        # uninstall master to start clean
        uninstall_server(master)
        # restore /etc/hosts
        etc_hosts = master.get_file_contents('/etc/hosts.bz1319912.backup')
        master.put_file_contents('/etc/hosts', etc_hosts)
        # restore /etc/hosts
        etc_hostname = master.get_file_contents('/etc/hostname.bz1319912.backup')

    def class_teardown(self, multihost):
        """ Full suite teardown """
        uninstall_server(multihost.master)
        uninstall_server(multihost.others[0])
