from subprocess import check_output, call
from shutil import copyfile, move
import pytest
from ipa_pytests.qe_install import uninstall_server, \
    set_resolv_conf_to_master, uninstall_client, \
    set_resolv_conf_add_server

monitor_ip_six = '2002::1'
master_ip_six = '2002::3'
replica_ip_six = '2002::4'
client_ip_six = '2002::5'
client_ip_six_two = '2002::50'
file_hosts = "/etc/hosts"
file_hosts_backup = "/etc/hosts.backup"
client_ip2 = "10.0.0.40"
sssd_conf_file = "/etc/sssd/sssd.conf"
sssd_local_file = "/tmp/sssd.conf"


class TestSSSDTests(object):

    def class_setup(self, multihost):
        """ Test sssd dynamic update with ipv4 2 addresses """
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
        """ get NIC name on client """
        get_dev_names = multihost.client.run_command(['ls', '/sys/class/net'],
                                                     raiseonerr=False)
        dev_names = get_dev_names.stdout_text.split('\n')
        for dev_name in dev_names:
            if dev_name not in ['lo', '']:
                global nic_client_device
                nic_client_device = dev_name
                break
            else:
                continue
            break

    def test_sssd_0001(self, multihost):
        """ Prepare env """
        print "Install ipa-server master"
        cmd1 = multihost.master.run_command([
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
        print "Prepare replica"
        cmd2 = multihost.master.run_command([
            'ipa-replica-prepare',
            '--ip-address=' + multihost.replica.ip,
            '--password', multihost.master.config.dirman_pw,
            multihost.replica.hostname])
        prepfile = '/var/lib/ipa/replica-info-' + \
                   multihost.replica.hostname + \
                   '.gpg'
        localfile = '/tmp/replica.file.tmp'
        multihost.master.transport.get_file(prepfile, localfile)
        multihost.replica.transport.put_file(localfile, prepfile)
        print "Install replica with file"
        cmd3 = multihost.replica.run_command([
            'ipa-replica-install',
            '--setup-dns',
            '--no-forwarders',
            '--admin-password', multihost.master.config.admin_pw,
            '--password', multihost.master.config.dirman_pw,
            '-U', prepfile])
        print "Prepare client"
        cmd4 = multihost.client.run_command([
            'ip', 'addr', 'add', client_ip2,
            'dev', nic_client_device])
        cmd5 = multihost.client.run_command([
            'ipa-client-install',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--server', multihost.master.hostname,
            '--principal', multihost.master.config.admin_id,
            '--password', multihost.master.config.admin_pw,
            '--hostname', multihost.client.hostname,
            '--force-join',
            '-U'])
        """ edit conf case no 1 """
        multihost.client.transport.get_file(sssd_conf_file, sssd_local_file)
        sssd_conf_var = ''
        with open(sssd_local_file, 'r') as fin:
            for line in fin:
                sssd_conf_var += str(line)
                domain_line = '[domain/' + multihost.master.domain.name + ']\n'
                if line == domain_line:
                    sssd_conf_var += str('dyndns_update = True\n')
                    sssd_conf_var += str('dyndns_iface = *\n')
        with open(sssd_local_file, 'w') as fout:
            fout.write(sssd_conf_var)
        multihost.client.transport.put_file(sssd_local_file, sssd_conf_file)
        cmd6 = multihost.client.run_command(['systemctl',
                                             'restart',
                                             'sssd.service'])
        multihost.master.kinit_as_admin()
        cmd7 = multihost.master.run_command(['ipa', 'dnsrecord-show',
                                             multihost.master.domain.name,
                                             multihost.client.shortname],
                                            raiseonerr=False)
        dns_check1 = 0
        dns_check2 = 0
        if multihost.client.ip in cmd7.stdout_text:
            dns_check1 = 1
        if client_ip2 in cmd7.stdout_text:
            dns_check2 = 1
        if dns_check1 == 1 and dns_check2 == 1:
            dns_result = 1
            assert 1 == dns_result
        else:
            dns_result = 0
            assert 1 == dns_result
        print cmd7.stdout_text

    def test_sssd_0002(self, multihost):
        """ Test sssd dynamic update with 2 ipv4 and one ipv6 addr """
        multihost.master.run_command(['ipa-server-install',
                                      '--uninstall', '-U'])
        multihost.replica.run_command(['ipa-server-install',
                                       '--uninstall', '-U'])
        multihost.client.run_command(['ipa-client-install',
                                      '--uninstall', '-U'])
        """ add ipv6 to test """
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

        """ add ipv6 to monitor """
        get_dev_names = check_output(['ls', '/sys/class/net'])
        dev_names = get_dev_names.split('\n')
        for dev_name in dev_names[:len(dev_names)-1]:
            if dev_name != 'lo':
                result = call(['ip', 'addr', 'add', monitor_ip_six + '/64',
                               'dev', dev_name])
                global monitor_dev_with_ip
                monitor_dev_with_ip = dev_name
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

        print "Install ipa-server master + ipv6"
        cmd1 = multihost.master.run_command([
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
        cmd2 = multihost.master.run_command([
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
        cmd3 = multihost.replica.run_command([
            'ipa-replica-install',
            '--setup-dns',
            '--no-forwarders',
            '--admin-password', multihost.master.config.admin_pw,
            '--password', multihost.master.config.dirman_pw,
            '-U', prepfile])
        print "Prepare client"
        cmd4 = multihost.client.run_command([
            'ipa-client-install',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--server', multihost.master.hostname,
            '--principal', multihost.master.config.admin_id,
            '--password', multihost.master.config.admin_pw,
            '--hostname', multihost.client.hostname,
            '--force-join',
            '-U'])
        multihost.client.transport.put_file(sssd_local_file, sssd_conf_file)
        multihost.client.run_command(['systemctl', 'restart', 'sssd.service'])
        multihost.master.kinit_as_admin()
        cmd5 = multihost.master.run_command([
            'ipa', 'dnsrecord-show',
            multihost.master.domain.name,
            multihost.client.shortname],
            raiseonerr=False)
        dns_check1 = 0
        dns_check2 = 0
        dns_check3 = 0
        if multihost.client.ip in cmd5.stdout_text:
            dns_check1 = 1
        if client_ip2 in cmd5.stdout_text:
            dns_check2 = 1
        if client_ip_six in cmd5.stdout_text:
            dns_check3 = 1
        if dns_check1 == 1 and dns_check2 == 1 and dns_check3 == 1:
            dns_result = 1
        else:
            dns_result = 0
        print cmd5.stdout_text
        assert dns_result == 1

    def test_sssd_0003(self, multihost):
        """ Test sssd dynamic update with 2 ipv6 addr """
        multihost.master.run_command(['ipa-server-install',
                                      '--uninstall', '-U'])
        multihost.replica.run_command(['ipa-server-install',
                                       '--uninstall', '-U'])
        multihost.client.run_command(['ipa-client-install',
                                      '--uninstall', '-U'])
        file_hosts_content = master_ip_six + ' ' + \
            multihost.master.hostname + '\n' + \
            replica_ip_six + ' ' + \
            multihost.replica.hostname + '\n' + \
            client_ip_six + ' ' + \
            multihost.client.hostname + '\n' + \
            '::1 ' + 'localhost' + '\n'

        multihost.master.transport.put_file_contents(file_hosts,
                                                     file_hosts_content)
        multihost.replica.transport.put_file_contents(file_hosts,
                                                      file_hosts_content)
        multihost.client.transport.put_file_contents(file_hosts,
                                                     file_hosts_content)

        """ remove transport """
        del multihost.master._transport
        del multihost.replica._transport
        del multihost.client._transport

        multihost.master.ip = master_ip_six
        multihost.master.external_hostname = master_ip_six
        multihost.replica.ip = replica_ip_six
        multihost.replica.external_hostname = replica_ip_six
        multihost.client.ip = client_ip_six
        multihost.client.external_hostname = client_ip_six

        """ resovl.conf to ipv6 """
        set_resolv_conf_to_master(multihost.client, multihost.master)
        set_resolv_conf_to_master(multihost.replica, multihost.master)

        print "removing ipv4"
        hosts = {multihost.master, multihost.replica, multihost.client}
        for host in hosts:
            get_dev_names = host.run_command(['ls', '/sys/class/net'],
                                             raiseonerr=False)
            dev_names = get_dev_names.stdout_text.split('\n')
            for dev_name in dev_names:
                if dev_name != '':
                    remove_ip4_cmd = host.run_command([
                        'ip', '-4', 'addr', 'flush', 'dev', dev_name])

        print "Install ipa-server master ipv6"
        cmd1 = multihost.master.run_command([
            'ipa-server-install', '--setup-dns',
            '--no-forwarders',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--hostname', multihost.master.hostname,
            '--ip-address', master_ip_six,
            '--admin-password', multihost.master.config.admin_pw,
            '--ds-password', multihost.master.config.dirman_pw,
            '-U'])
        print "Prepare replica"""
        cmd2 = multihost.master.run_command([
            'ipa-replica-prepare',
            '--ip-address', replica_ip_six,
            '--password', multihost.master.config.dirman_pw,
            multihost.replica.hostname])
        prepfile = '/var/lib/ipa/replica-info-' + \
                   multihost.replica.hostname + '.gpg'
        localfile = '/tmp/replica.file.tmp'
        multihost.master.transport.get_file(prepfile, localfile)
        multihost.replica.transport.put_file(localfile, prepfile)
        print "Install replica with file"
        cmd3 = multihost.replica.run_command([
            'ipa-replica-install',
            '--setup-dns',
            '--no-forwarders',
            '--admin-password', multihost.master.config.admin_pw,
            '--password', multihost.master.config.dirman_pw,
            '-U', prepfile])
        print "Prepare client"
        cmd4 = multihost.client.run_command([
            'ip', 'addr', 'add', client_ip_six_two, 'dev', nic_client_device])
        cmd5 = multihost.client.run_command([
            'ipa-client-install',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--server', multihost.master.hostname,
            '--principal', multihost.master.config.admin_id,
            '--password', multihost.master.config.admin_pw,
            '--hostname', multihost.client.hostname,
            '--force-join',
            '-U'])
        multihost.client.transport.put_file(sssd_local_file, sssd_conf_file)
        multihost.client.run_command(['systemctl', 'restart', 'sssd.service'])
        multihost.master.kinit_as_admin()
        cmd6 = multihost.master.run_command([
            'ipa', 'dnsrecord-show',
            multihost.master.domain.name,
            multihost.client.shortname],
            raiseonerr=False)
        dns_check1 = 0
        dns_check2 = 0
        if client_ip_six in cmd6.stdout_text:
            dns_check1 = 1
        if client_ip_six_two in cmd6.stdout_text:
            dns_check2 = 1
        if dns_check1 == 1 and dns_check2 == 1:
            dns_result = 1
        else:
            dns_result = 0
        assert dns_result == 1, "ip not in dns"
        print cmd6.stdout_text

    def class_teardown(self, multihost):
        """ let ipv6 only envirnment for next modules """
