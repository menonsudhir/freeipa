from subprocess import call
import pytest
from ipa_pytests.qe_install import uninstall_server, \
    set_resolv_conf_to_master, uninstall_client
from ipa_pytests.shared.utils import get_ipv6_ip

tuser = "tuser"
tpassword = "Password123"


class TestIPv6Tests(object):

    def class_setup(self, multihost):

        global master_ip_six
        global replica_ip_six
        global client_ip_six

        master_ip_six = get_ipv6_ip(multihost.master)
        replica_ip_six = get_ipv6_ip(multihost.replica)
        client_ip_six = get_ipv6_ip(multihost.client)
        print("Master ip :")
        print(master_ip_six)

        print("Replica ip :")
        print(replica_ip_six)

        print("Client ip :")
        print(client_ip_six)

        print("changing variables")
        multihost.master.ip = master_ip_six
        multihost.master.external_hostname = master_ip_six
        multihost.replica.ip = replica_ip_six
        multihost.replica.external_hostname = replica_ip_six
        multihost.client.ip = client_ip_six
        multihost.client.external_hostname = client_ip_six

        print("uninstall")
        """ Uninstall if ipa installed """
        uninstall_client(multihost.client)
        uninstall_server(multihost.replica)
        cmdun3 = multihost.master.run_command(['ipa-server-install', '--uninstall', '-U',
                                               '--ignore-last-of-role'], raiseonerr=False)

        """ resolv.conf on replica and client to point on master """
        set_resolv_conf_to_master(multihost.client, multihost.master)
        set_resolv_conf_to_master(multihost.replica, multihost.master)

    def test_ipv6_0001(self, multihost):
        """
        IDM-IPA-TC: IPV6: Install ipa-server
        """
        print("Install ipa-server")
        params1 = [
            'ipa-server-install',
            '--setup-dns',
            '--no-forwarders',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--hostname', multihost.master.hostname,
            '--ip-address', multihost.master.ip,
            '--admin-password', multihost.master.config.admin_pw,
            '--ds-password', multihost.master.config.dirman_pw,
            '-U']
        print("RUNCMD:", ' '.join(params1))
        cmd = multihost.master.run_command(params1, raiseonerr=False)

    def test_ipv6_0002(self, multihost):
        """
        IDM-IPA-TC: IPV6: Install ipa-server replica
        """
        print("Prepare replica - install client")
        multihost.master.kinit_as_admin()
        multihost.master.run_command([
            'ipa',
            'dnsconfig-mod',
            '--allow-sync-ptr=true'])
        params2 = [
            'ipa-client-install',
            '--principal', 'admin',
            '--password', multihost.master.config.admin_pw,
            '--force-join',
            '--ip-address=' + replica_ip_six,
            '--domain', multihost.master.domain.name,
            '-U']
        print("RUNCMD:", ' '.join(params2))
        cmd2 = multihost.replica.run_command(params2, raiseonerr=False)

        print("Install replica - promote")
        params3 = [
            'ipa-replica-install',
            '--setup-dns',
            '--no-forwarders',
            '--admin-password', multihost.master.config.admin_pw,
            '--password', multihost.master.config.dirman_pw,
            '--domain', multihost.master.domain.name,
            '-U']
        print("RUNCMD:", ' '.join(params3))
        cmd3 = multihost.replica.run_command(params3, raiseonerr=False)

    def test_ipv6_0003(self, multihost):
        """
        IDM-IPA-TC: IPV6: Install ipa-client
        """
        print("Install ipa-client and join")
        params4 = [
            'ipa-client-install',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--server', multihost.master.hostname,
            '--principal', multihost.master.config.admin_id,
            '--password', multihost.master.config.admin_pw,
            '--hostname', multihost.client.hostname,
            '--force-join',
            '-U']
        print("RUNCMD:", ' '.join(params4))
        cmd = multihost.client.run_command(params4, raiseonerr=False)

    def test_ipv6_0004(self, multihost):
        """
        IDM-IPA-TC: IPV6: create user on master and edit on replica and login
        """
        print("Create user on master")
        multihost.master.kinit_as_admin()
        cmd_prepare = multihost.master.run_command([
            'ipa', 'user-add',
            '--first', 'Test',
            '--last', 'User',
            tuser])

        print("Edit user on replica")
        multihost.replica.kinit_as_admin()
        cmd = multihost.replica.run_command([
            'ipa', 'user-mod',
            '--password', tuser],
            stdin_text=tpassword)
        print("Login with test user from client")
        ldap_exp_change = "dn: uid=" + tuser + \
            ",cn=users,cn=accounts,dc=testrelm,dc=test" + '\n' \
            "changetype: modify" + '\n' \
            "replace: krbPasswordExpiration" + '\n' \
            "krbPasswordExpiration: 20201231011529Z" + '\n'
        print(ldap_exp_change)
        multihost.master.kinit_as_admin()
        ldap_change = multihost.master.run_command([
            'ldapmodify', '-x',
            '-D', 'cn=directory manager',
            '-w', multihost.master.config.dirman_pw],
            stdin_text=ldap_exp_change)
        print("kinit")
        cmd1 = multihost.client.kinit_as_user(tuser, tpassword)

    def test_ipv6_0005(self, multihost):
        """
        IDM-IPA-TC: IPV6: remove user on replica
        """
        print("remove user")
        cmd = multihost.replica.run_command(['ipa', 'user-del', tuser])

    def test_ipv6_0006(self, multihost):
        """
        IDM-IPA-TC: IPV6: Uninstall client and re-install client and join
        """
        print("Uninstall client")
        cmd_uninstall = multihost.client.run_command(['ipa-client-install',
                                                      '--uninstall', '-U'])
        print("REinstall client")
        params5 = [
            'ipa-client-install',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--server', multihost.master.hostname,
            '--principal', multihost.master.config.admin_id,
            '--password', multihost.master.config.admin_pw,
            '--hostname', multihost.client.hostname,
            '--force-join',
            '-U']
        print("RUNCMD:", ' '.join(params5))
        cmd_install = multihost.client.run_command(params5, raiseonerr=False)

    def class_teardown(self, multihost):
        pass
