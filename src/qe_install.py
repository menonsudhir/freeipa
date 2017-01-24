#!/usr/bin/python

""" QE Install
This provides the necessary functions to setup IPA Servers and Clients.
"""

from __future__ import print_function
import pytest
import time
import re
import ipa_pytests.shared.paths
from ipa_pytests.shared.utils import service_control
from ipa_pytests.shared.rpm_utils import list_rpms
from ipa_pytests.shared.utils import get_domain_level
from ipa_pytests.shared.utils import ipa_version_gte
from ipa_pytests.shared.log_utils import backup_logs


def disable_firewall(host):
    """ Disable firewalld or iptables """
    if host.transport.file_exists('/etc/init.d/iptables'):
        service_control(host, 'iptables', 'stop')
        service_control(host, 'iptables', 'off')

    if host.transport.file_exists('/etc/init.d/ip6tables'):
        service_control(host, 'ip6tables', 'stop')
        service_control(host, 'ip6tables', 'off')

    if host.transport.file_exists('/usr/lib/systemd/system/firewalld.service'):
        service_control(host, 'firewalld', 'stop')
        service_control(host, 'firewalld', 'off')


def set_hostname(host):
    """ Set system hostname to what plugin has listed for configuration """
    if host.transport.file_exists('/etc/hostname'):
        host.run_command(['cp', '-af',
                          '/etc/hostname',
                          '/etc/hostname.qebackup'])
        host.put_file_contents('/etc/hostname', host.hostname)
        host.run_command(['hostnamectl'])
    else:
        host.run_command(['cp', '-af', '/etc/sysconfig/network',
                          '/etc/sysconfig/network.qebackup'])
        contents = host.get_file_contents('/etc/sysconfig/network')
        contents = re.sub('HOSTNAME=.*$',
                          'HOSTNAME=%s' % re.escape(host.hostname), contents)
        print("SYSCONFIG_NETWORK = \n%s" % contents)
        host.put_file_contents('/etc/sysconfig/network', contents)
        host.run_command(['hostname', host.hostname])


def set_etc_hosts(host):
    """ Set /etc/hosts entry for host.ip host.hostname """
    etc_hosts = host.get_file_contents('/etc/hosts')
    host.put_file_contents('/etc/hosts.set_etc_hosts.backup', etc_hosts)
    for remove in [host.ip, host.hostname]:
        etc_hosts = re.sub(r'^.*\b%s\n.*$' % remove,
                           '',
                           etc_hosts,
                           flags=re.MULTILINE)
    etc_hosts += '\n%s %s\n' % (host.ip, host.hostname)
    host.put_file_contents('/etc/hosts', etc_hosts)


def set_resolv_conf_to_master(host, master):
    """ Set resolv.conf nameserver to point to master ip address """
    host.run_command(['cp', '-af',
                      '/etc/resolv.conf',
                      '/etc/resolv.conf.qebackup'])
    host.run_command(['chattr', '-i', '/etc/resolv.conf'])
    host.put_file_contents('/etc/resolv.conf', 'nameserver ' + master.ip)
    cmd = host.run_command('cat /etc/resolv.conf')
    print("resolv.conf: %s" % cmd.stdout_text)


def set_resolv_conf_add_server(host, server_ip):
    """ Add a nameserver to resolv.conf """
    cfg = host.get_file_contents('/etc/resolv.conf')
    cfg = cfg + "\nnameserver " + server_ip
    host.put_file_contents('/etc/resolv.conf', cfg)


def set_rngd(host):
    """ install and configure rngd if virt """
    cpuinfo = host.get_file_contents('/proc/cpuinfo')
    if 'QEMU' not in cpuinfo and 'hypervisor' not in cpuinfo:
        print("Not a known Virt...not installing RNGD")
        return
    host.yum_install(['rng-tools'])
    if host.transport.file_exists('/etc/rc.d/init.d/rngd'):
        rng_cfg = 'EXTRAOPTIONS="-r /dev/urandom"\n'
        cfg_file = '/etc/sysconfig/rngd'
        host.put_file_contents(cfg_file, rng_cfg)
    elif host.transport.file_exists('/usr/lib/systemd/system/rngd.service'):
        cfg_file = '/usr/lib/systemd/system/rngd.service'
        rng_cmd = 'ExecStart=/sbin/rngd -f -r /dev/urandom\n'
        rng_cfg = host.get_file_contents(cfg_file)
        new_cfg = re.sub(r'ExecStart=.*\n', rng_cmd, rng_cfg)
        host.put_file_contents(cfg_file, new_cfg)
        host.run_command(['systemctl', 'daemon-reload'])
    else:
        print("Not a known service system type...skipping service start")
        return
    sleep(3)
    service_control(host, 'rngd', 'on')
    service_control(host, 'rngd', 'stop')
    service_control(host, 'rngd', 'start')
    cmd = service_control(host, 'rngd', 'status')
    if cmd.returncode != 0:
        print("WARNING: rngd did not start properly...tests may run slow")
        print("STDOUT: ", cmd.stdout_text)


def setup_master(master, setup_reverse=True):
    """
    This is the default testing setup for an IPA Master.
    This setup routine will install an IPA Master with DNS and a forwarder.
    The domain and realm will be set differently than the real DNS domain.
    """
    revnet = master.ip.split('.')[2] + '.' + \
        master.ip.split('.')[1] + '.' + \
        master.ip.split('.')[0] + '.in-addr.arpa.'

    list_rpms(master)
    disable_firewall(master)
    set_hostname(master)
    set_etc_hosts(master)
    set_rngd(master)

    print_time()
    master.yum_install(['ipa-server', 'ipa-server-dns',
                        'bind-dyndb-ldap', 'bind-pkcs11',
                        'bind-pkcs11-utils'])

    print_time()
    runcmd = ['ipa-server-install',
              '--setup-dns',
              '--forwarder', master.config.dns_forwarder,
              '--domain', master.domain.name,
              '--realm', master.domain.realm,
              # '--hostname', master.hostname,
              # '--ip-address', master.ip,
              '--admin-password', master.config.admin_pw,
              '--ds-password', master.config.dirman_pw,
              # '--mkhomedir',
              '-U']
    if not setup_reverse:
        runcmd.append('--no-reverse')
    else:
        runcmd.extend(['--reverse-zone', revnet])
        # only add allow-zone-overlap if IPA >= 4.4.0
        if ipa_version_gte(master, '4.4.0'):
            runcmd.extend(['--allow-zone-overlap'])

    print("RUNCMD:", ' '.join(runcmd))
    cmd = master.run_command(runcmd, raiseonerr=False)

    print("STDOUT:", cmd.stdout_text)
    print("STDERR:", cmd.stderr_text)
    print_time()
    if cmd.returncode != 0:
        backup_logs(master, ['/var/log/ipaserver-install.log',
                             '/var/log/ipaclient-install.log',
                             '/var/log/ipaupgrade.log'])
        raise ValueError("ipa-server-install failed with "
                         "error code=%s" % cmd.returncode)


def setup_replica_prepare_file(replica, master):
    """ create the replica prepare file for Domain Level 0 environments """
    runcmd = ['ipa-replica-prepare',
              '-p', master.config.admin_pw,
              '--ip-address', replica.ip,
              '--reverse-zone', replica.revnet,
              replica.hostname]
    print("RUNCMD:", ' '.join(runcmd))
    cmd = master.run_command(runcmd, raiseonerr=False)

    print("STDOUT:", cmd.stdout_text)
    print("STDERR:", cmd.stderr_text)
    print("TIME:", time.strftime('%H:%M:%S', time.localtime()))
    if cmd.returncode != 0:
        raise ValueError("ipa-replica-prepare failed "
                         "with error code=%s" % cmd.returncode)

    prepfile = '/var/lib/ipa/replica-info-' + replica.hostname + '.gpg'
    prep_content = master.get_file_contents(prepfile)
    replica.put_file_contents(prepfile, prep_content)


def setup_replica(replica, master, setup_dns=True, setup_ca=True, setup_reverse=True):
    """
    This is the default testing setup for an IPA Replica.  This setup routine
    will install an IPA Replica with DNS and a forwarder.  The domain and realm
    will be set differently than the real DNS domain.  Also, it does setup the
    replica as a CA.
    :type setup_ca: True or False
    :type setup_dns: True or False
    :type setup_reverse: True or False
    """
    replica.revnet = replica.ip.split('.')[2] + '.' + \
        replica.ip.split('.')[1] + '.' + \
        replica.ip.split('.')[0] + '.in-addr.arpa.'
    master.revnet = master.ip.split('.')[2] + '.' + \
        master.ip.split('.')[1] + '.' + \
        master.ip.split('.')[0] + '.in-addr.arpa.'

    if replica.revnet != master.revnet:
        setup_dns_revnet = True
    else:
        setup_dns_revnet = False
    print("SETUPDNSREVNET = %s" % setup_dns_revnet)

    print("Listing RPMS")
    list_rpms(replica)
    print("Disabling Firewall")
    disable_firewall(replica)
    print("Setting hostname")
    set_hostname(replica)
    print("Setting /etc/hosts")
    set_etc_hosts(replica)
    print("Setting up RNGD")
    set_rngd(replica)
    if setup_dns:
        set_resolv_conf_to_master(replica, master)

    print_time()
    replica.yum_install(['ipa-server', 'ipa-server-dns', 'bind-dyndb-ldap',
                         'bind-pkcs11', 'bind-pkcs11-utils'])

    domain_level = get_domain_level(master)
    if domain_level == 0:
        print("Domain Level is 0 so we have to use prepare files")
        print_time()
        setup_replica_prepare_file(replica, master)
    else:
        print("Domain Level is 1 so we do not need a prep file")
        master.kinit_as_admin()
        cmd = master.run_command(['ipa', 'dnsrecord-add',
                                  master.domain.name,
                                  ''.join(replica.hostname.split('.')[:1]),
                                  '--a-rec', replica.ip,
                                  '--a-create-reverse'], raiseonerr=False)

    sleep(5)
    set_resolv_conf_to_master(replica, master)
    params = ['ipa-replica-install', '-U']

    print_time()
    if setup_dns:
        params.extend(['--setup-dns',
                       '--forwarder', master.config.dns_forwarder])
        if setup_reverse and setup_dns_revnet:
            params.extend(['--reverse-zone', replica.revnet])
            # only add allow-zone-overlap if IPA >= 4.4.0
            if ipa_version_gte(master, '4.4.0'):
                params.extend(['--allow-zone-overlap'])

    if not setup_reverse:
        params.append('--no-reverse')

    if setup_ca:
        params.append('--setup-ca')

    # params.extend(['--ip-address', replica.ip])
    params.extend(['--server', master.hostname])
    params.extend(['--domain', master.domain.name])
    params.extend(['--admin-password', master.config.admin_pw])

    if domain_level == 0:
        prepfile = '/var/lib/ipa/replica-info-' + replica.hostname + '.gpg'
        params.extend(['--password', master.config.dirman_pw])
        params.extend([prepfile])
    else:
        params.extend(['--principal', master.config.admin_id])

    print("RUNCMD:", ' '.join(params))
    cmd = replica.run_command(params, raiseonerr=False)
    print("STDOUT: %s" % cmd.stdout_text)
    print("STDERR: %s" % cmd.stderr_text)
    print_time()
    if cmd.returncode != 0:
        backup_logs(replica, ['/var/log/ipareplica-install.log',
                              '/var/log/ipaclient-install.log',
                              '/var/log/ipareplica-conncheck.log'])
        raise ValueError("ipa-replica-install failed with "
                         "error code=%s" % cmd.returncode)


def setup_client(client, master, server=None, domain=None):
    """
    This is the default testing setup for an IPA Client.
    This setup routine will install an IPA client using autodiscovery.
    """

    print_time()
    client.yum_install(['ipa-client', 'ipa-admintools'])

    list_rpms(client)
    disable_firewall(client)
    set_hostname(client)
    set_etc_hosts(client)
    set_rngd(client)
    sleep(5)
    set_resolv_conf_to_master(client, master)

    print_time()
    runcmd = ['ipa-client-install', '-U',
              '--principal', 'admin',
              '--password', master.config.admin_pw]

    if server and domain:
        runcmd.extend(['--server', master.hostname])
        runcmd.extend(['--domain', master.domain.name])

    print("RUNCMD:", ' '.join(runcmd))
    cmd = client.run_command(runcmd, raiseonerr=False)

    print("STDOUT:", cmd.stdout_text)
    print("STDERR:", cmd.stderr_text)
    print_time()
    if cmd.returncode != 0:
        backup_logs(client, ['/var/log/ipaclient-install.log'])
        raise ValueError("ipa-client-install failed with "
                         "error code=%s" % cmd.returncode)


def uninstall_server(host):
    """
    This is the default uninstall for a master or replica.  It merely runs
    the standard server uninstall command.
    """
    if host.transport.file_exists('/etc/ipa/default.conf'):
        runcmd = ['ipa-server-install',
                  '--uninstall',
                  '-U']
        cmd = host.run_command(runcmd, raiseonerr=False)
        print("Uninstalling IPA server on machine [%s]" % host.hostname)
        print("STDOUT: %s" % cmd.stdout_text)
        print("STDERR: %s" % cmd.stderr_text)
        if cmd.returncode != 0:
            raise ValueError("%s failed with error "
                             "code=%s" % (" ".join(runcmd), cmd.returncode))
    else:
        print("/etc/ipa/default.conf not found...skipped --uninstall")


def uninstall_client(host):
    """
    This is the default uninstall for a client.  It runs the standard client
    uninstall command.
    """
    if host.transport.file_exists('/etc/ipa/default.conf'):
        runcmd = ['ipa-client-install', '--uninstall', '-U']
        cmd = host.run_command(runcmd, raiseonerr=False)
        print("Running command: %s" % " ".join(runcmd))
        print("STDOUT: %s" % cmd.stdout_text)
        print("STDERR: %s" % cmd.stderr_text)
        if cmd.returncode == 2:
            print("Client not installed")
        elif cmd.returncode != 0:
            raise ValueError("Command [%s] failed with error "
                             "code=%s" % (" ".join(runcmd), cmd.returncode))
    else:
        print("/etc/ipa/default.conf not found...skipped --uninstall")


def adtrust_install(host):
    """ Prepare an IPA server to establish trust relationships with AD """
    cmd = 'cat /etc/redhat-release | grep "Atomic"'
    command = host.run_command(cmd, raiseonerr=False)
    if command.returncode != 0:
        print("Host is not an Atomic host.")
        runcmd = 'rpm -q ipa-server-trust-ad'
        print("Running command: %s" % runcmd)
        cmd = host.run_command(runcmd, raiseonerr=False)
        print("STDOUT: %s" % cmd.stdout_text)
        print("STDERR: %s" % cmd.stderr_text)
        if 'package ipa-server-trust-ad is not installed' in cmd.stderr_text:
            runcmd = 'yum install -y ipa-server-trust-ad'
            cmd = host.run_command(runcmd, raiseonerr=False)
            print("Running command: %s" % runcmd)
            if cmd.returncode != 0:
                pytest.fail("Unable to install ipa-server-trust-ad RPM on master")
        else:
            netbios = (host.domain.realm).split(".")[0]
            print("NetBIOS name for master : %s " % netbios)
            runcmd = 'ipa-adtrust-install --netbios-name=' + netbios + \
                     ' -a ' + host.config.admin_pw + ' -U'
            print("Running command: %s" % runcmd)
            cmd = host.run_command(runcmd, raiseonerr=False)
            print("STDOUT: %s" % cmd.stdout_text)
            print("STDERR: %s" % cmd.stderr_text)
            if cmd.returncode != 0:
                pytest.fail("IPA ad trust install failed on "
                            "master [%s]" % host.hostname)
    else:
        """ Prepare an IPA Docker server to establish trust relationships with AD """
        print("Host is an Atomic host.")
        runcmd = 'docker exec -it ipadocker rpm -q ipa-server-trust-ad < /dev/ptmx'
        cmd = host.run_command(runcmd, raiseonerr=False)
        print("STDOUT:", cmd.stdout_text)
        print("STDERR:", cmd.stderr_text)
        if 'package ipa-server-trust-ad is not installed' in cmd.stderr_text:
            pytest.fail("Package for ad trust not installed")
        else:
            netbios = (host.domain.realm).split(".")[0]
            print("NetBIOS name for master : %s " % netbios)
            dockercmd = 'docker exec -it ipadocker'
            runcmd = dockercmd + \
                     ' ipa-adtrust-install --netbios-name=' + netbios + \
                     ' -a ' + host.config.admin_pw + ' -U < /dev/ptmx'
            print("Running command: %s" % runcmd)
            cmd = host.run_command(runcmd, raiseonerr=False)
            print("STDOUT: %s" % cmd.stdout_text)
            print("STDERR: %s" % cmd.stderr_text)
            if cmd.returncode != 0:
                pytest.fail("IPA-DOCKER ad trust install failed on "
                            "master [%s]" % host.hostname)
            else:
                print("IPA-Docker installed with ad trust successfully.")


def print_time():
    """
    Helper function to Local Time in given format
    """
    print("TIME: %s" % time.strftime('%H:%M:%S', time.localtime()))


def sleep(seconds=1):
    """
    Helper function to sleep for desired seconds and notifiy user about same
    """
    print("Sleeping for [%d] seconds" % seconds)
    time.sleep(seconds)
