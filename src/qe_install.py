#!/usr/bin/python

""" QE Install
This provides the necessary functions to setup IPA Servers and Clients.
"""

import time
import re


def disable_firewall(host):
    """ Disable firewalld or iptables """
    if host.transport.file_exists('/etc/init.d/iptables'):
        host.run_command(['service', 'iptables', 'stop'])
        host.run_command(['chkconfig', 'iptables', 'off'])

    if host.transport.file_exists('/etc/init.d/ip6tables'):
        host.run_command(['service', 'ip6tables', 'stop'])
        host.run_command(['chkconfig', 'ip6tables', 'off'])

    if host.transport.file_exists('/usr/lib/systemd/system/firewalld.service'):
        host.run_command(['systemctl', 'stop', 'firewalld.service'])
        host.run_command(['systemctl', 'disable', 'firewalld.service'])


def set_hostname(host):
    """ Set system hostname to what plugin has listed for configuration """
    if host.transport.file_exists('/etc/hostname'):
        host.run_command(['cp', '-af', '/etc/hostname', '/etc/hostname.qebackup'])
        host.put_file_contents('/etc/hostname', host.hostname)
    else:
        host.run_command(['cp', '-af', '/etc/sysconfig/network',
                          '/etc/sysconfig/network.qebackup'])
        contents = host.get_file_contents('/etc/sysconfig/network')
        contents = re.sub('HOSTNAME=.*$', 'HOSTNAME=%s' % re.escape(host.hostname), contents)
        print "SYSCONFIG_NETWORK = \n%s" % contents
        host.put_file_contents('/etc/sysconfig/network', contents)
        host.run_command(['hostname', host.hostname])


def set_resolv_conf_to_master(host, master):
    """ Set resolv.conf nameserver to point to master ip address """
    host.run_command(['cp', '-af', '/etc/resolv.conf', '/etc/resolv.conf.qebackup'])
    host.put_file_contents('/etc/resolv.conf', 'nameserver ' + master.ip)
    cmd = host.run_command('cat /etc/resolv.conf')
    print "resolv.conf:"
    print cmd.stdout_text


def set_rngd(host):
    """ install and configure rngd if virt """
    cpuinfo = host.get_file_contents('/proc/cpuinfo')
    if 'QEMU' not in cpuinfo:
        print "Not a known Virt...not installing RNGD"
        return
    host.run_command(['yum', '-y', '--nogpgcheck', 'install', 'rng-tools'])
    if host.transport.file_exists('/etc/rc.d/init.d/rngd'):
        # rng_cfg = 'EXTRAOPTIONS="-r /dev/urandom -t 5"\n'
        rng_cfg = 'EXTRAOPTIONS="-r /dev/urandom"\n'
        cfg_file = '/etc/sysconfig/rngd'
    elif host.transport.file_exists('/usr/lib/systemd/system/rngd.service'):
        rng_cfg = '[Service]\nExecStart=\nExecStart=/sbin/rngd -f -r /dev/urandom\n'
        cfg_file = '/etc/systemd/system/rngd.service.d/entropy-source.conf'
        host.transport.make_recursive('/etc/systemd/system/rngd.service.d')
    else:
        print "Not a known service system type...skipping service start"
        return
    host.put_file_contents(cfg_file, rng_cfg)
    host.run_command(['service', 'rngd', 'start'])
    host.run_command(['chkconfig', 'rngd', 'on'])


def setup_master(master):
    """
    This is the default testing setup for an IPA Master.  This setup routine
    will install an IPA Master with DNS and a forwarder.  The domain and realm
    will be set differently than the real DNS domain.
    """

    disable_firewall(master)
    set_hostname(master)
    set_rngd(master)

    cmd = master.run_command(['yum', '-y', '--nogpgcheck', 'install', 'ipa-server', 'bind-dyndb-ldap'])
    print cmd.stdout_text
    print cmd.stderr_text

    cmd = master.run_command(['ipa-server-install',
                              '--setup-dns',
                              '--forwarder', master.config.dns_forwarder,
                              '--domain', master.domain.name,
                              '--realm', master.domain.realm,
                              '--hostname', master.hostname,
                              '--ip-address', master.ip,
                              '--admin-password', master.config.admin_pw,
                              '--ds-password', master.config.dirman_pw,
                              # '--mkhomedir',
                              '-U'], raiseonerr=False)

    print "STDOUT:", cmd.stdout_text
    print "STDERR:", cmd.stderr_text
    if cmd.returncode != 0:
        raise ValueError("ipa-server-install failed with error code=%s" % cmd.returncode)


def setup_replica(replica, master):
    """
    This is the default testing setup for an IPA Replica.  This setup routine
    will install an IPA Replica with DNS and a forwarder.  The domain and realm
    will be set differently than the real DNS domain.  Also, it does setup the
    replica as a CA.
    """
    revnet = replica.ip.split('.')[2] + '.' + \
        replica.ip.split('.')[1] + '.' + \
        replica.ip.split('.')[0] + '.in-addr.arpa.'

    disable_firewall(replica)
    set_hostname(replica)
    set_rngd(replica)

    cmd = replica.run_command(['yum', '-y', '--nogpgcheck', 'install', 'ipa-server',
                               'bind-dyndb-ldap'])
    print cmd.stdout_text
    print cmd.stderr_text

    cmd = master.run_command(['ipa-replica-prepare',
                              '-p', master.config.admin_pw,
                              '--ip-address', replica.ip,
                              '--reverse-zone', revnet,
                              replica.hostname], raiseonerr=False)

    print "STDOUT:", cmd.stdout_text
    print "STDERR:", cmd.stderr_text
    if cmd.returncode != 0:
        raise ValueError("ipa-replica-prepare failed with error code=%s" % cmd.returncode)

    prepfile = '/var/lib/ipa/replica-info-' + replica.hostname + '.gpg'
    prep_content = master.get_file_contents(prepfile)
    replica.put_file_contents(prepfile, prep_content)

    time.sleep(5)
    set_resolv_conf_to_master(replica, master)

    cmd = replica.run_command(['ipa-replica-install',
                               '--setup-dns',
                               '--forwarder', master.config.dns_forwarder,
                               '--admin-password', master.config.admin_pw,
                               '--password', master.config.dirman_pw,
                               # '--mkhomedir',
                               '-U', prepfile], raiseonerr=False)

    print "STDOUT:", cmd.stdout_text
    print "STDERR:", cmd.stderr_text
    if cmd.returncode != 0:
        raise ValueError("ipa-replica-install failed with error code=%s" % cmd.returncode)


def setup_client(client, master):
    """
    This is the default testing setup for an IPA Client.  This setup routine
    will install an IPA client using autodiscovery.
    """

    cmd = client.run_command(['yum', '-y', '--nogpgcheck', 'install', 'ipa-client'])
    print cmd.stdout_text
    print cmd.stderr_text

    disable_firewall(client)
    set_hostname(client)
    set_rngd(client)
    time.sleep(5)
    set_resolv_conf_to_master(client, master)

    cmd = client.run_command(['ipa-client-install',
                              '--principal', 'admin',
                              '--password', master.config.admin_pw,
                              '-U'], raiseonerr=False)

    print "STDOUT:", cmd.stdout_text
    print "STDERR:", cmd.stderr_text
    if cmd.returncode != 0:
        raise ValueError("ipa-client-install failed with error code=%s" % cmd.returncode)


def uninstall_server(host):
    """
    This is the default uninstall for a master or replica.  It merely runs
    the standard server uninstall command.
    """
    cmd = host.run_command(['ipa-server-install', '--uninstall', '-U'], raiseonerr=False)

    print "STDOUT:", cmd.stdout_text
    print "STDERR:", cmd.stderr_text
    if cmd.returncode != 0:
        raise ValueError("ipa-server-install --uninstall failed with error code=%s" % cmd.returncode)


def uninstall_client(host):
    """
    This is the default uninstall for a client.  It runs the standard client
    uninstall command.
    """
    cmd = host.run_command(['ipa-client-install', '--uninstall', '-U'], raiseonerr=False)

    print "STDOUT:", cmd.stdout_text
    print "STDERR:", cmd.stderr_text
    if cmd.returncode == 2:
        print "Client not installed"
    elif cmd.returncode != 0:
        raise ValueError("ipa-client-install --uninstall failed with error code=%s" % cmd.returncode)
