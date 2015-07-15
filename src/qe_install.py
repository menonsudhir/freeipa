#!/usr/bin/python

""" QE Install
This provides the necessary functions to setup IPA Servers and Clients.
"""

import time
import re
from ipa_pytests.shared.utils import service_control
from ipa_pytests.shared.utils import list_rpms


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
    host.run_command(['chattr', '-i', '/etc/resolv.conf'])
    host.put_file_contents('/etc/resolv.conf', 'nameserver ' + master.ip)
    cmd = host.run_command('cat /etc/resolv.conf')
    print "resolv.conf:"
    print cmd.stdout_text


def set_resolv_conf_add_server(host, server_ip):
    """ Add a nameserver to resolv.conf """
    cfg = host.get_file_contents('/etc/resolv.conf')
    cfg = cfg + "\nnameserver " + server_ip
    host.put_file_contents('/etc/resolv.conf', cfg)


def set_rngd(host):
    """ install and configure rngd if virt """
    cpuinfo = host.get_file_contents('/proc/cpuinfo')
    if 'QEMU' not in cpuinfo and 'hypervisor' not in cpuinfo:
        print "Not a known Virt...not installing RNGD"
        return
    host.yum_install(['rng-tools'])
    if host.transport.file_exists('/etc/rc.d/init.d/rngd'):
        # rng_cfg = 'EXTRAOPTIONS="-r /dev/urandom -t 5"\n'
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
        print "Not a known service system type...skipping service start"
        return
    time.sleep(3)
    service_control(host, 'rngd', 'on')
    service_control(host, 'rngd', 'stop')
    service_control(host, 'rngd', 'start')
    cmd = service_control(host, 'rngd', 'status')
    if cmd.returncode != 0:
        print "WARNING: rngd did not start properly...tests may run slow"
        print "STDOUT: ", cmd.stdout_text


def setup_master(master):
    """
    This is the default testing setup for an IPA Master.  This setup routine
    will install an IPA Master with DNS and a forwarder.  The domain and realm
    will be set differently than the real DNS domain.
    """

    list_rpms(master)
    disable_firewall(master)
    set_hostname(master)
    set_rngd(master)

    print "TIME:", time.strftime('%H:%M:%S', time.localtime())
    master.yum_install(['ipa-server', 'bind-dyndb-ldap', 'bind-pkcs11', 'bind-pkcs11-utils'])

    print "TIME:", time.strftime('%H:%M:%S', time.localtime())
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
    print "TIME:", time.strftime('%H:%M:%S', time.localtime())
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

    list_rpms(replica)
    disable_firewall(replica)
    set_hostname(replica)
    set_rngd(replica)

    print "TIME:", time.strftime('%H:%M:%S', time.localtime())
    replica.yum_install(['ipa-server', 'bind-dyndb-ldap', 'bind-pkcs11', 'bind-pkcs11-utils'])

    print "TIME:", time.strftime('%H:%M:%S', time.localtime())
    cmd = master.run_command(['ipa-replica-prepare',
                              '-p', master.config.admin_pw,
                              '--ip-address', replica.ip,
                              '--reverse-zone', revnet,
                              replica.hostname], raiseonerr=False)

    print "STDOUT:", cmd.stdout_text
    print "STDERR:", cmd.stderr_text
    print "TIME:", time.strftime('%H:%M:%S', time.localtime())
    if cmd.returncode != 0:
        raise ValueError("ipa-replica-prepare failed with error code=%s" % cmd.returncode)

    prepfile = '/var/lib/ipa/replica-info-' + replica.hostname + '.gpg'
    prep_content = master.get_file_contents(prepfile)
    replica.put_file_contents(prepfile, prep_content)

    time.sleep(5)
    set_resolv_conf_to_master(replica, master)

    print "TIME:", time.strftime('%H:%M:%S', time.localtime())
    cmd = replica.run_command(['ipa-replica-install',
                               '--setup-ca',
                               '--setup-dns',
                               '--forwarder', master.config.dns_forwarder,
                               '--admin-password', master.config.admin_pw,
                               '--password', master.config.dirman_pw,
                               # '--mkhomedir',
                               '-U', prepfile], raiseonerr=False)

    print "STDOUT:", cmd.stdout_text
    print "STDERR:", cmd.stderr_text
    print "TIME:", time.strftime('%H:%M:%S', time.localtime())
    if cmd.returncode != 0:
        raise ValueError("ipa-replica-install failed with error code=%s" % cmd.returncode)


def setup_client(client, master):
    """
    This is the default testing setup for an IPA Client.  This setup routine
    will install an IPA client using autodiscovery.
    """

    print "TIME:", time.strftime('%H:%M:%S', time.localtime())
    client.yum_install(['ipa-client', 'ipa-admintools'])

    list_rpms(client)
    disable_firewall(client)
    set_hostname(client)
    set_rngd(client)
    time.sleep(5)
    set_resolv_conf_to_master(client, master)

    print "TIME:", time.strftime('%H:%M:%S', time.localtime())
    cmd = client.run_command(['ipa-client-install',
                              '--principal', 'admin',
                              '--password', master.config.admin_pw,
                              '-U'], raiseonerr=False)

    print "STDOUT:", cmd.stdout_text
    print "STDERR:", cmd.stderr_text
    print "TIME:", time.strftime('%H:%M:%S', time.localtime())
    if cmd.returncode != 0:
        raise ValueError("ipa-client-install failed with error code=%s" % cmd.returncode)


def uninstall_server(host):
    """
    This is the default uninstall for a master or replica.  It merely runs
    the standard server uninstall command.
    """
    if host.transport.file_exists('/etc/ipa/default.conf'):
        cmd = host.run_command(['ipa-server-install', '--uninstall', '-U'], raiseonerr=False)
        print "STDOUT:", cmd.stdout_text
        print "STDERR:", cmd.stderr_text
        if cmd.returncode != 0:
            raise ValueError("ipa-server-install --uninstall failed with error code=%s" % cmd.returncode)
    else:
        print "/etc/ipa/default.conf not found...skipped --uninstall"


def uninstall_client(host):
    """
    This is the default uninstall for a client.  It runs the standard client
    uninstall command.
    """
    if host.transport.file_exists('/etc/ipa/default.conf'):
        cmd = host.run_command(['ipa-client-install', '--uninstall', '-U'], raiseonerr=False)
        print "STDOUT:", cmd.stdout_text
        print "STDERR:", cmd.stderr_text
        if cmd.returncode == 2:
            print "Client not installed"
        elif cmd.returncode != 0:
            raise ValueError("ipa-client-install --uninstall failed with error code=%s" % cmd.returncode)
    else:
        print "/etc/ipa/default.conf not found...skipped --uninstall"
