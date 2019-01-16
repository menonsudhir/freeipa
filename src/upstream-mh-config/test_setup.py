"""
-Setting hostname and /etc/hosts of test vms
"""

from __future__ import print_function
import yaml
import sys
import subprocess


def _call_ssh(host, cmd):
    subprocess.check_call(
        ["ssh", "-o StrictHostKeyChecking=no", "root@" + host['ip'], cmd]
    )


def _create_ui_test_conf(host, domain, admin, password):
    """
    Create ui_test.conf for running Selenium tests.
    """
    # TODO: some options could be passed from mh_cfg_* (realm, paths and flags)
    conf = [
        ('ipa_admin', admin),
        ('ipa_password', password),
        ('ipa_server', host['name']),
        ('ipa_ip', host['ip']),
        ('ipa_domain', domain['name']),
        ('ipa_realm', 'TESTRELM.TEST'),
        ('has_kra', True),
        ('type', 'local'),
        ('browser', 'firefox'),
        ('save_screenshots', True),
        ('screenshot_dir', '~/screenshots/'),
        ('geckodriver_log_path', '~/geckodriver.log'),
    ]

    conf_text = '\n'.join('%s: %s' % opt for opt in conf)

    _call_ssh(host, 'mkdir -p ~/.ipa && echo -e "%s" > ~/.ipa/ui_test.conf'
              % conf_text)


def _install_master(host, domain, forwarder, password):
    _call_ssh(
        host,
        'ipa-server-install'
        ' --setup-dns'
        ' --setup-kra'
        ' --forwarder {forwarder}'
        ' --domain {domain[name]}'
        ' --realm TESTRELM.TEST'
        ' --hostname {host[name]}'
        ' --ip-address {host[ip]}'
        ' --auto-reverse'
        ' -p {password} -a {password} -U'
        .format(
            domain=domain,
            host=host,
            forwarder=forwarder,
            password=password
        )
    )
    _call_ssh(host, 'cp /etc/ipa/default.conf ~/.ipa/default.conf')


with open((sys.argv[1:])[0]) as stream:
    try:
        code = yaml.load(stream)
        domain = code['domains'][0]
        password = code['admin_pw']
        hosts = domain['hosts']
        no_of_hosts = len(hosts)
        for host in hosts:

            # /etc/hosts setup on sut
            etchostname = "echo "+host['name']+" > /etc/hostname"
            _call_ssh(host, etchostname)
            print(etchostname)
            cmd = []
            for j in range(no_of_hosts):
                if j is 0:
                    cmd.append("echo %(ip)s %(name)s > /etc/hosts" % hosts[j])
                else:
                    cmd.append("echo %(ip)s %(name)s >> /etc/hosts" % hosts[j])
            print(cmd)
            for k in range(no_of_hosts):
                print(cmd[k])
                _call_ssh(host, cmd[k])

            # Setup resolv.conf on client machine
            if host['role'] == "client":
                print(host['role'])
                resolv = []
                for j in range(no_of_hosts):
                    if hosts[j]['role'] != "client":
                        if j is 0:
                            resolv.append("echo nameserver %(ip)s > /etc/resolv.conf" % hosts[j])
                        else:
                            resolv.append("echo nameserver %(ip)s >> /etc/resolv.conf" % hosts[j])
                print(resolv)
                for k in range(no_of_hosts):
                    if hosts[k]['role'] == "client":
                        for item in resolv:
                            _call_ssh(hosts[k], item)
            elif host['role'] == "master":
                _create_ui_test_conf(host, domain, code['admin_id'], password)
                if host.get('install_master'):
                    _install_master(host, domain, code['dns_forwarder'], password)
    except yaml.YAMLError as exc:
        print(exc)
