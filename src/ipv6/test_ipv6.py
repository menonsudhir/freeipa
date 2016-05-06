#!/usr/bin/python

from shutil import copyfile, move
from subprocess import check_output, call

monitor_ip_six = '2002::1'
master_ip_six = '2002::3'
replica_ip_six = '2002::4'
client_ip_six = '2002::5'
file_hosts = "/etc/hosts"
file_hosts_backup = "/etc/hosts.backup"
file_resolv = "/etc/resolv.conf"
file_resolv_backup = "/etc/resolv.conf.backup"


class TestIPv6Tests(object):

    def class_setup(self, multihost):

        """ Uninstall if ipa installed """
        install_check_m = multihost.master.run_command(['ipactl', 'status'], raiseonerr=False)
        if install_check_m.returncode == 0:
            multihost.master.run_command(['ipa-server-install', '--uninstall', '-U'])
        install_check_r = multihost.replica.run_command(['ipactl', 'status'], raiseonerr=False)
        if install_check_r.returncode == 0:
            multihost.replica.run_command(['ipa-server-install', '--uninstall', '-U'])
        multihost.client.run_command(['ipa-client-install', '-uninstall', '-U'], raiseonerr=False)

        hosts = { multihost.master : master_ip_six, multihost.replica : replica_ip_six, multihost.client : client_ip_six}
        for host in hosts.keys():
            get_dev_names = host.run_command(['ls', '/sys/class/net'], raiseonerr=False)
            dev_names = get_dev_names.stdout_text.split('\n')
            
            for dev_name in dev_names:
                if dev_name not in ['lo', '']:
                    print "ipv6 to " + host + " : " + dev_name
                    set_master_ip_cmd = host.run_command(['ip', 'addr', 'add', hosts[host] + '/64', 'dev', dev_name])
                    break
                else:
                    continue
                break

        """ Backup and set up new hosts file on master """
        del hosts
        hosts = { mulithost.master, multihost.replica, multihost.client }
        for host in hosts:
            backup_hosts_cmp = host.run_command(['cp', '-p', file_hosts, file_hosts_backup])

        file_hosts_content = master_ip_six + ' ' + multihost.master.hostname + '\n' + \
            replica_ip_six + ' ' + multihost.replica.hostname + '\n' + \
            client_ip_six + ' ' + multihost.client.hostname + '\n' + \
            '::1 ' + 'localhost'

        multihost.master.transport.put_file_contents(file_hosts,file_hosts_content)
        multihost.replica.transport.put_file_contents(file_hosts,file_hosts_content)
        multihost.client.transport.put_file_contents(file_hosts,file_hosts_content)

        """ resolv.conf on replica and client to point on master """
        if multihost.replica.transport.file_exists(file_resolv):
            multihost.replica.run_command(['cp', '-p', file_resolv, file_resolv_backup])
        if multihost.client.transport.file_exists(file_resolv):
            multihost.client.run_command(['cp', '-p', file_resolv, file_resolv_backup])

        file_resolv_client_content = 'nameserver ' + master_ip_six
        multihost.replica.transport.put_file_contents(file_resolv,file_resolv_client_content)
        multihost.client.transport.put_file_contents(file_resolv,file_resolv_client_content)

        """ add ipv6 to monitor """
        get_dev_names = check_output(['ls', '/sys/class/net'])
        dev_names = get_dev_names.split('\n')
        for dev_name in dev_names[:len(dev_names)-1]:
            if dev_name != 'lo':
                result = call(['ip', 'addr', 'add', monitor_ip_six + '/64', 'dev', dev_name])
                global monitor_dev_with_ip
                monitor_dev_with_ip = dev_name
                break
            else:
                continue
            break

        """ remove transport """
        print "removing _transport"
        del multihost.master._transport
        del multihost.replica._transport
        del multihost.client._transport

        print "changing variables"
        multihost.master.ip = master_ip_six
        multihost.master.external_hostname = master_ip_six
        multihost.replica.ip = replica_ip_six
        multihost.replica.external_hostname = replica_ip_six
        multihost.client.ip = client_ip_six
        multihost.client.external_hostname = client_ip_six

        """ Remove IPV4 from machines """
        print "removing ipv4"
        hosts = { multihost.master, multihost.replica, multihost.client }
        for host in hosts:
            get_dev_names = host.run_command(['ls', '/sys/class/net'], raiseonerr=False)
            dev_names = get_dev_names.stdout_text.split('\n')
            
            for dev_name in dev_names:
                if dev_name not in ['lo', '']:
                    print "ipv6 to " + host + " : " + dev_name
                    remove_ip4_cmd = host.run_command(['ip', '-4', 'addr', 'flush', 'dev', dev_name])
                    break
                else:
                    continue
                break

    def test_ipv6_0001(self, multihost):
        """
        IDM-IPA-TC: IPV6: Install ipa-server
        """
        print "Install ipa-server"
        cmd = multihost.master.run_command(['ipa-server-install', '--setup-dns',
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
        prepare = multihost.master.run_command(['ipa-replica-prepare',
            '--ip-address=' + multihost.replica.ip,
            '--password', multihost.master.config.dirman_pw,
            multihost.replica.hostname],raiseonerr=False)
        prepfile = '/var/lib/ipa/replica-info-' + multihost.replica.hostname + '.gpg'
        localfile = '/tmp/replica.file.tmp'
        multihost.master.transport.get_file(prepfile, localfile )
        multihost.replica.transport.put_file(localfile, prepfile)
        print "Install replica with file"
        cmd = multihost.replica.run_command(['ipa-replica-install',
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
        cmd = multihost.client.run_command(['ipa-client-install',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--server', multihost.master.hostname,
            '--principal', multihost.master.config.admin_id,
            '--password', multihost.master.config.admin_pw,
            '--hostname', multihost.client.hostname,
            '--force-join',
            '-U'],raiseonerr=False)

    def test_ipv6_0004(self, multihost):
        """
        IDM-IPA-TC: IPV6: create user on master and edit on replica
        """
        print "Create user on master"
        multihost.master.kinit_as_admin()
        cmd_prepare = multihost.master.run_command(['ipa', 'user-add',
            '--first', 'Test',
            '--last', 'User',
            'tuser'])

        print "Edit user on replica"
        multihost.replica.kinit_as_admin()
        cmd = multihost.replica.run_command(['ipa', 'user-mod',
            '--password', 'tuser'],
            stdin_text='Password123')
        print "Login with test user from client"
        cmd = multihost.client.qe_run(['kinit', 'tuser'], stdin_text=tuser)


    def test_ipv6_0005(self, multihost):
        """
        IDM-IPA-TC: IPV6: remove user on replica
        """
        print "remove user"
        cmd = multihost.replica.run_command(['ipa', 'user-del', 'tuser'])

    def test_ipv6_0006(self, multihost):
        """
        IDM-IPA-TC: IPV6: Uninstall client and re-install client and join
        """
        print "Uninstall client"
        cmd_uninstall = multihost.client.run_command(['ipa-client-install',
                                                      '--uninstall', '-U'])
        print "REinstall client"
        cmd_install = multihost.client.run_command(['ipa-client-install',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--server', multihost.master.hostname,
            '--principal', multihost.master.config.admin_id,
            '--password', multihost.master.config.admin_pw,
            '--hostname', multihost.client.hostname,
            '--force-join',
            '-U'],raiseonerr=False)


    def class_teardown(self, multihost):
        """ Uninstall if ipa installed """
        install_check_m = multihost.master.run_command(['ipactl', 'status'],raiseonerr=False)
        if install_check_m.returncode == 0 :
            multihost.master.run_command(['ipa-server-install', '--uninstall', '-U'])
        install_check_r = multihost.replica.run_command(['ipactl', 'status'],raiseonerr=False)
        if install_check_r.returncode == 0 :
            multihost.replica.run_command(['ipa-server-install', '--uninstall', '-U'])
        multihost.client.run_command(['ipa-client-install', '-uninstall', '-U'],raiseonerr=False)
        """ restore resolv file """
        if multihost.replica.transport.file_exists(file_resolv_backup):
            multihost.replica.run_command(['cp', '-p', file_resolv_backup, file_resolv])
        if multihost.client.transport.file_exists(file_resolv):
            multihost.client.run_command(['cp', '-p', file_resolv_backup, file_resolv])
        """ restore hosts file """
        hosts = { mulithost.master, multihost.replica, multihost.client }
        for host in hosts:
            backup_hosts_cmp = host.run_command(['cp', '-p', file_hosts_backup, file_hosts])

