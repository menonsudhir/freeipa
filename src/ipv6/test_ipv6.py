#!/usr/bin/python

from subprocess import call
import pytest
from ipa_pytests.qe_install import uninstall_server, \
    set_resolv_conf_to_master, uninstall_client

monitor_ip_six = '2002::1'
master_ip_six = '2002::3'
replica_ip_six = '2002::4'
client_ip_six = '2002::5'
tuser = "tuser"
tpassword = "Password123"


class TestIPv6Tests(object):

    def class_setup(self, multihost):

        print "changing variables"
        multihost.master.ip = master_ip_six
        multihost.master.external_hostname = master_ip_six
        multihost.replica.ip = replica_ip_six
        multihost.replica.external_hostname = replica_ip_six
        multihost.client.ip = client_ip_six
        multihost.client.external_hostname = client_ip_six

        print "uninstall"
        """ Uninstall if ipa installed """
        uninstall_server(multihost.master)
        uninstall_server(multihost.replica)
        uninstall_client(multihost.client)

        """ resolv.conf on replica and client to point on master """
        set_resolv_conf_to_master(multihost.client, multihost.master)
        set_resolv_conf_to_master(multihost.replica, multihost.master)

    def test_ipv6_0001(self, multihost):
        """
        IDM-IPA-TC: IPV6: Install ipa-server
        """
        print "Install ipa-server"
        cmd = multihost.master.run_command([
            'ipa-server-install',
            '--setup-dns',
            '--no-forwarders',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--hostname', multihost.master.hostname,
            '--ip-address', multihost.master.ip,
            '--admin-password', multihost.master.config.admin_pw,
            '--ds-password', multihost.master.config.dirman_pw,
            '-U'])

    def test_ipv6_0002(self, multihost):
        """
        IDM-IPA-TC: IPV6: Install ipa-server replica
        """
        print "Prepare replica file"
        prepare = multihost.master.run_command([
            'ipa-replica-prepare',
            '--ip-address=' + multihost.replica.ip,
            '--password', multihost.master.config.dirman_pw,
            multihost.replica.hostname])
        prepfile = '/var/lib/ipa/replica-info-' + multihost.replica.hostname \
            + '.gpg'
        localfile = '/tmp/replica.file.tmp'
        multihost.master.transport.get_file(prepfile, localfile)
        multihost.replica.transport.put_file(localfile, prepfile)
        print "Install replica with file"
        cmd = multihost.replica.run_command([
            'ipa-replica-install',
            '--setup-dns',
            '--no-forwarders',
            '--admin-password', multihost.master.config.admin_pw,
            '--password', multihost.master.config.dirman_pw,
            '-U', prepfile])

    def test_ipv6_0003(self, multihost):
        """
        IDM-IPA-TC: IPV6: Install ipa-client
        """
        print "Install ipa-client and join"
        cmd = multihost.client.run_command([
            'ipa-client-install',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--server', multihost.master.hostname,
            '--principal', multihost.master.config.admin_id,
            '--password', multihost.master.config.admin_pw,
            '--hostname', multihost.client.hostname,
            '--force-join',
            '-U'])

    def test_ipv6_0004(self, multihost):
        """
        IDM-IPA-TC: IPV6: create user on master and edit on replica and login
        """
        print "Create user on master"
        multihost.master.kinit_as_admin()
        cmd_prepare = multihost.master.run_command([
            'ipa', 'user-add',
            '--first', 'Test',
            '--last', 'User',
            tuser])

        print "Edit user on replica"
        multihost.replica.kinit_as_admin()
        cmd = multihost.replica.run_command([
            'ipa', 'user-mod',
            '--password', tuser],
            stdin_text=tpassword)
        print "Login with test user from client"
        ldap_exp_change = "dn: uid=" + tuser + \
            ",cn=users,cn=accounts,dc=testrelm,dc=test" + '\n' \
            "changetype: modify" + '\n' \
            "replace: krbPasswordExpiration" + '\n' \
            "krbPasswordExpiration: 20201231011529Z" + '\n'
        print ldap_exp_change
        multihost.master.kinit_as_admin()
        ldap_change = multihost.master.run_command([
            'ldapmodify', '-x',
            '-D', 'cn=directory manager',
            '-w', multihost.master.config.dirman_pw],
            stdin_text=ldap_exp_change)
        print "kinit"
        cmd1 = multihost.client.kinit_as_user(tuser, tpassword)

    def test_ipv6_0005(self, multihost):
        """
        IDM-IPA-TC: IPV6: remove user on replica
        """
        print "remove user"
        cmd = multihost.replica.run_command(['ipa', 'user-del', tuser])

    def test_ipv6_0006(self, multihost):
        """
        IDM-IPA-TC: IPV6: Uninstall client and re-install client and join
        """
        print "Uninstall client"
        cmd_uninstall = multihost.client.run_command(['ipa-client-install',
                                                      '--uninstall', '-U'])
        print "REinstall client"
        cmd_install = multihost.client.run_command([
            'ipa-client-install',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--server', multihost.master.hostname,
            '--principal', multihost.master.config.admin_id,
            '--password', multihost.master.config.admin_pw,
            '--hostname', multihost.client.hostname,
            '--force-join',
            '-U'])

    def class_teardown(self, multihost):
        pass
