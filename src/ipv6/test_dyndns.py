"""
This is a quick test for ipv6 scenarios.
It requires MRC setup with ipv6 enabled environment as well as
all test cases are going to run on another controller environment.
"""
from subprocess import check_output, call
from shutil import copyfile, move
import pytest
from ipa_pytests.qe_install import uninstall_server, \
    set_resolv_conf_to_master, uninstall_client, \
    set_resolv_conf_add_server, set_hostname, set_etc_hosts
from ipa_pytests.qe_install import disable_firewall
from ipa_pytests.qe_install import dns_record_add
from collections import namedtuple
from ipa_pytests.shared.utils import get_ipv6_ip
import time


monitor_ip_six = '2002::2'
client_ip_six_two = '2002::40'
file_hosts = "/etc/hosts"
file_hosts_backup = "/etc/hosts.backup"
client_ip2 = "10.0.0.50"
sssd_conf_file = "/etc/sssd/sssd.conf"
sssd_local_file = "/tmp/sssd.conf"


class TestSSSDTests(object):

    def class_setup(self, multihost):
        """ Test sssd dynamic update with ipv4 2 addresses """
        """ 1st time setup """
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

        multihost.master.yum_install(['ipa-server', 'ipa-server-dns'])
        multihost.replica.yum_install(['ipa-server', 'ipa-server-dns'])
        multihost.client.yum_install(['ipa-client'])

        """ Uninstall if ipa installed """
        uninstall_client(multihost.client)
        uninstall_server(multihost.replica)
        uninstall_server(multihost.master)

        print("Disabling Firewall on master, replica, client")

        disable_firewall(multihost.master)
        disable_firewall(multihost.replica)
        disable_firewall(multihost.client)

        print("Setting hostname on master, replica, client")

        set_hostname(multihost.master)
        set_hostname(multihost.replica)
        set_hostname(multihost.client)

        print("Setting /etc/hosts on master, replica, client")

        set_etc_hosts(multihost.master)
        set_etc_hosts(multihost.replica)
        set_etc_hosts(multihost.client)

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
        """ IDM-IPA-TC: IPV6: Prepare env """
        print("Install ipa-server master")

        params = [
            'ipa-server-install',
            '--setup-dns', '--no-forwarders',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--hostname', multihost.master.hostname,
            '--ip-address', multihost.master.ip,
            '--auto-reverse',
            '-p', multihost.master.config.admin_pw,
            '-a', multihost.master.config.admin_pw,
            '-U']
        print("RUNCMD:", ' '.join(params))
        cmd1 = multihost.master.run_command(params, raiseonerr=False)

        print("Prepare replica - install client")
        multihost.master.kinit_as_admin()
        multihost.master.run_command([
            'ipa',
            'dnsconfig-mod',
            '--allow-sync-ptr=true'])

        params1 = [
            'ipa-client-install',
            '--ip-address=' + multihost.replica.ip,
            '--principal', 'admin',
            '--password', multihost.master.config.admin_pw,
            '--domain', multihost.master.domain.name,
            '--server', multihost.master.hostname,
            '-U']
        print("RUNCMD:", ' '.join(params1))
        cmd2 = multihost.replica.run_command(params1, raiseonerr=False)
        print("Install replica - promote to replica")

        cmd = dns_record_add(multihost.master,
                             multihost.master.domain.name,
                             multihost.replica.shortname,
                             'A',
                             [multihost.replica.ip])
        time.sleep(5)
        set_resolv_conf_to_master(multihost.replica, multihost.master)

        cmdstr = [
            'ipa-replica-install',
            '--setup-dns',
            '--no-forwarders',
            '--admin-password', multihost.master.config.admin_pw,
            '--password', multihost.master.config.dirman_pw,
            '--domain', multihost.master.domain.name,
            '-U']
        print("RUNCMD:", ' '.join(cmdstr))
        cmd3 = multihost.replica.run_command(cmdstr, raiseonerr=False)

        print("Prepare client")

        cmd4 = multihost.client.run_command([
            'ip', 'addr', 'add', client_ip2,
            'dev', nic_client_device])

        cmdstr2 = [
            'ipa-client-install',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--server', multihost.master.hostname,
            '--principal', multihost.master.config.admin_id,
            '--password', multihost.master.config.admin_pw,
            '--hostname', multihost.client.hostname,
            '--force-join',
            '-U']
        print("RUNCMD:", ' '.join(cmdstr2))
        cmd5 = multihost.client.run_command(cmdstr2, raiseonerr=False)

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
        print(cmd7.stdout_text)

    def test_sssd_0002(self, multihost):
        """ IDM-IPA-TC: IPV6: add ipv6 to monitor """
        uninstall_client(multihost.client)
        uninstall_server(multihost.replica)
        cmdun1 = multihost.master.run_command(['ipa-server-install', '--uninstall', '-U',
                                               '--ignore-last-of-role'], raiseonerr=False)

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

        print("Install ipa-server master - multihomed")
        params2 = [
            'ipa-server-install',
            '--setup-dns', '--no-forwarders',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--hostname', multihost.master.hostname,
            '--ip-address', multihost.master.ip,
            '--ip-address', master_ip_six,
            '--auto-reverse',
            '-p', multihost.master.config.admin_pw,
            '-a', multihost.master.config.admin_pw,
            '-U']
        print("RUNCMD:", ' '.join(params2))
        cmd1 = multihost.master.run_command(params2, raiseonerr=False)

        print("Prepare replica - install client")

        multihost.master.kinit_as_admin()

        multihost.master.run_command([
            'ipa',
            'dnsconfig-mod',
            '--allow-sync-ptr=true'])
        params3 = [
            'ipa-client-install',
            '--ip-address=' + multihost.replica.ip,
            '--ip-address=' + replica_ip_six,
            '--principal', 'admin',
            '--password', multihost.master.config.admin_pw,
            '--domain', multihost.master.domain.name,
            '-U']
        print("RUNCMD:", ' '.join(params3))
        cmd2 = multihost.replica.run_command(params3, raiseonerr=False)

        print("Install replica - promote to replica")
        time.sleep(5)
        set_resolv_conf_to_master(multihost.replica, multihost.master)
        params4 = [
            'ipa-replica-install',
            '--setup-dns',
            '--no-forwarders',
            '--admin-password', multihost.master.config.admin_pw,
            '--password', multihost.master.config.dirman_pw,
            '--domain', multihost.master.domain.name,
            '-U']
        print("RUNCMD:", ' '.join(params4))
        cmd3 = multihost.replica.run_command(params4, raiseonerr=False)

        print("Prepare client")

        params5 = [
            'ipa-client-install',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--principal', multihost.master.config.admin_id,
            '--password', multihost.master.config.admin_pw,
            '--hostname', multihost.client.hostname,
            '--force-join',
            '-U']
        print("RUNCMD:", ' '.join(params5))
        cmd4 = multihost.client.run_command(params5, raiseonerr=False)

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
        print(cmd5.stdout_text)
        assert dns_result == 1

    def test_sssd_0003(self, multihost):
        """ IDM-IPA-TC: IPV6: Test sssd dynamic update with 2 ipv6 addr """
        uninstall_client(multihost.client)
        uninstall_server(multihost.replica)
        cmdun2 = multihost.master.run_command(['ipa-server-install', '--uninstall', '-U',
                                               '--ignore-last-of-role'], raiseonerr=False)
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

        print("removing ipv4")
        hosts = {multihost.master, multihost.replica, multihost.client}
        for host in hosts:
            get_dev_names = host.run_command(['ls', '/sys/class/net'],
                                             raiseonerr=False)
            dev_names = get_dev_names.stdout_text.split('\n')
            for dev_name in dev_names:
                if dev_name != '':
                    remove_ip4_cmd = host.run_command([
                         'ip', '-4', 'addr', 'flush', 'dev', dev_name])
                    if remove_ip4_cmd.returncode == 0:
                        print("ipv4 address removed")
                    else:
                        pytest.fail("not able to remove ipv4 address")

        print("Install ipa-server master ipv6 only")

        params6 = [
            'ipa-server-install',
            '--setup-dns', '--no-forwarders',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--hostname', multihost.master.hostname,
            '--ip-address', master_ip_six,
            '--auto-reverse',
            '-p', multihost.master.config.admin_pw,
            '-a', multihost.master.config.admin_pw,
            '-U']
        print("RUNCMD:", ' '.join(params6))
        cmd1 = multihost.master.run_command(params6, raiseonerr=False)

        print("Prepare replica - install client")
        multihost.master.kinit_as_admin()
        multihost.master.run_command([
            'ipa',
            'dnsconfig-mod',
            '--allow-sync-ptr=true'])

        params7 = [
            'ipa-client-install',
            '--principal', 'admin',
            '--password', multihost.master.config.admin_pw,
            '--force-join',
            '--ip-address=' + replica_ip_six,
            '--domain', multihost.master.domain.name,
            '-U']
        print("RUNCMD:", ' '.join(params7))
        cmd2 = multihost.replica.run_command(params7, raiseonerr=False)

        print("Install replica - promote to replica")

        params8 = [
            'ipa-replica-install',
            '--setup-dns',
            '--no-forwarders',
            '--admin-password', multihost.master.config.admin_pw,
            '--password', multihost.master.config.dirman_pw,
            '--domain', multihost.master.domain.name,
            '-U']
        print("RUNCMD:", ' '.join(params8))
        cmd3 = multihost.replica.run_command(params8,raiseonerr=False)

        print("Prepare client")
        cmd4 = multihost.client.run_command([
            'ip', 'addr', 'add', client_ip_six_two, 'dev', nic_client_device])

        params9 = [
            'ipa-client-install',
            '--domain', multihost.master.domain.name,
            '--realm', multihost.master.domain.realm,
            '--principal', multihost.master.config.admin_id,
            '--password', multihost.master.config.admin_pw,
            '--hostname', multihost.client.hostname,
            '--force-join',
            '-U']
        print("RUNCMD:", ' '.join(params9))
        cmd5 = multihost.client.run_command(params9,raiseonerr=False)

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
        print(cmd6.stdout_text)

    def class_teardown(self, multihost):
        """ let ipv6 only envirnment for next modules """
