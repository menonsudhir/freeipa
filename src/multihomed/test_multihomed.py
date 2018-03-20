from time import sleep
import pytest
from ipa_pytests.qe_install import uninstall_server, \
    set_resolv_conf_to_master, uninstall_client, \
    set_resolv_conf_add_server
from ipa_pytests.shared.utils import service_control

monitor_ip_six = '2002::1'
master_ip_six = '2002::3'
replica_ip_six = '2002::4'
client_ip_six = '2002::5'
client_ip2 = '10.0.0.40'
file_hosts = '/etc/hosts'
sssd_conf_file = '/etc/sssd/sssd.conf'
sssd_local_file = '/tmp/sssd.conf'


class TestMultihomedTests(object):

    def class_setup(self, multihost):
        """ 1st time setup """
        multihost.master.yum_install(['ipa-server', 'ipa-server-dns'])
        multihost.replica.yum_install(['ipa-server', 'ipa-server-dns'])
        multihost.client.yum_install(['ipa-client'])

        """ Uninstall if ipa installed """
        uninstall_server(multihost.master)
        uninstall_server(multihost.replica)
        uninstall_client(multihost.client)
        """ set up resovl.conf """
        set_resolv_conf_to_master(multihost.client, multihost.master)
        set_resolv_conf_to_master(multihost.replica, multihost.master)

        hosts = {multihost.master: master_ip_six,
                 multihost.replica: replica_ip_six,
                 multihost.client: client_ip_six}
        for host in hosts.keys():
            get_dev_names = host.run_command(['ls', '/sys/class/net'],
                                             raiseonerr=False)
            dev_names = get_dev_names.stdout_text.split('\n')
            for dev_name in dev_names:
                if dev_name not in ['lo', '']:
                    print "ipv6 to " + host.hostname + " : " + dev_name
                    set_master_ip_cmd = host.run_command([
                        'ip', 'addr', 'add', hosts[host] + '/64',
                        'dev', dev_name])
                    break
                else:
                    continue
                break

        """ new hosts file """
        file_hosts_content = master_ip_six + ' ' + multihost.master.hostname + '\n' + \
            replica_ip_six + ' ' + multihost.replica.hostname + '\n' + \
            client_ip_six + ' ' + multihost.client.hostname + '\n' + \
            '::1 ' + 'localhost' + '\n' + \
            '127.0.0.1 ' + 'localhost' + '\n' + \
            multihost.master.ip + ' ' + multihost.master.hostname + '\n' + \
            multihost.replica.ip + ' ' + multihost.replica.hostname + '\n' + \
            multihost.client.ip + ' ' + multihost.client.hostname + '\n'

        multihost.master.transport.put_file_contents(
            file_hosts, file_hosts_content)
        multihost.replica.transport.put_file_contents(
            file_hosts, file_hosts_content)
        multihost.client.transport.put_file_contents(
            file_hosts, file_hosts_content)

        set_resolv_conf_add_server(multihost.replica, master_ip_six)
        set_resolv_conf_add_server(multihost.client, master_ip_six)

    def test_multihomed_0001(self, multihost):
        """IDM-IPA-TC : Multihomed : update of ipv6 along with ipv4 when client install"""

        print "Install ipa-server master + ipv6"
        multihost.master.qerun([
            'ipa-server-install', '--setup-dns',
            '--no-forwarders',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--hostname', multihost.master.hostname,
            '--ip-address', multihost.master.ip,
            '--ip-address', master_ip_six,
            '--admin-password', multihost.master.config.admin_pw,
            '--ds-password', multihost.master.config.dirman_pw,
            '-U'])
        print "Prepare replica"""
        multihost.master.qerun([
            'ipa-replica-prepare',
            '--ip-address=' + multihost.replica.ip,
            '--ip-address', replica_ip_six,
            '--password', multihost.master.config.dirman_pw,
            multihost.replica.hostname])
        prepfile = '/var/lib/ipa/replica-info-' + \
                   multihost.replica.hostname + '.gpg'
        localfile = '/tmp/replica.file.tmp'
        multihost.master.transport.get_file(prepfile, localfile)
        multihost.replica.transport.put_file(localfile, prepfile)
        print "Install replica with file"
        multihost.replica.qerun([
            'ipa-replica-install',
            '--setup-dns',
            '--no-forwarders',
            '--admin-password', multihost.master.config.admin_pw,
            '--password', multihost.master.config.dirman_pw,
            '-U', prepfile])
        print "Prepare client"
        multihost.client.qerun([
            'ipa-client-install',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--server', multihost.master.hostname,
            '--principal', multihost.master.config.admin_id,
            '--password', multihost.master.config.admin_pw,
            '--hostname', multihost.client.hostname,
            '--force-join',
            '-U'])
        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command([
            'ipa', 'dnsrecord-show',
            multihost.master.domain.name,
            multihost.client.shortname])
        dns_check1 = 0
        dns_check2 = 0
        if multihost.client.ip in cmd.stdout_text:
            dns_check1 = 1
        if client_ip_six in cmd.stdout_text:
            dns_check2 = 1
        if dns_check1 == 1 and dns_check2 == 1:
            dns_result = 1
        else:
            dns_result = 0
        print cmd.stdout_text
        assert dns_result == 1, "Both IP in DNS updated!"

    def test_multihomed_0002(self, multihost):
        """IDM-IPA-TC : Multihomed : remove dns record and client sssd restart with dyn_update = True"""
        multihost.master.kinit_as_admin()
        print "remove dns record"
        multihost.master.qerun([
            'ipa',
            'dnsrecord-del',
            multihost.master.domain.name,
            multihost.client.shortname,
            '--del-all'
            ])
        print "check"
        sssd_conf_var = ''
        multihost.client.transport.get_file(sssd_conf_file, sssd_local_file,)
        with open(sssd_local_file, 'r') as fin:
            for line in fin:
                sssd_conf_var += str(line)
                domain_line = '[domain/' + multihost.master.domain.name + ']\n'
                if line == domain_line:
                    sssd_conf_var += str('dyndns_update = true\n')
        with open(sssd_local_file, 'w') as fout:
            fout.write(sssd_conf_var)
        multihost.client.transport.put_file(sssd_local_file, sssd_conf_file)
        print "sssd restart"
        service_control(multihost.client, 'sssd', 'restart')
        sleep(10)
        cmd = multihost.master.run_command([
            'ipa',
            'dnsrecord-show',
            multihost.master.domain.name,
            multihost.client.shortname])
        print cmd.stdout_text
        dns_check1 = 0
        dns_check2 = 0
        if multihost.client.ip in cmd.stdout_text:
            dns_check1 = 1
        if client_ip_six in cmd.stdout_text:
            dns_check2 = 1
        if dns_check1 == 1 and dns_check2 == 1:
            dns_result = 1
        else:
            dns_result = 0
        assert dns_result == 1, "Both IP in DNS NOT updated!"

    def class_teardown(self, multihost):
        hosts = {multihost.master: master_ip_six,
                 multihost.replica: replica_ip_six,
                 multihost.client: client_ip_six}
        for host in hosts.keys():
            get_dev_names = host.run_command(['ls', '/sys/class/net'],
                                             raiseonerr=False)
            dev_names = get_dev_names.stdout_text.split('\n')
            for dev_name in dev_names:
                if dev_name not in ['lo', '']:
                    print "remove ipv6"
                    set_master_ip_cmd = host.run_command([
                        'ip', '-6', 'addr', 'del', hosts[host] + '/64',
                        'dev', dev_name])
                    break
                else:
                    continue
                break
