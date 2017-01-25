"""
Major shared support utility functions
- kinit_as_uesr - kinit as user with password
- qerun - utility function to run command on host and check output
- qe_http_get - experimental function to get web page
- qe_http_krb_get - experimental function to get web page with kerb ticket
- ldapmodify - ldapmodify command
- run_pk12util - Helper function to run pk12util
- create_noise_file - Helper function to create randomness in a file
"""
import time
import re
import pytest
import os
import tempfile
import paths
import array
import string
import random
from distutils.version import StrictVersion


def kinit_as_user(host, user, passwd):
    """ Kinit as user with password """
    host.run_command('kdestroy -A')
    host.run_command(['kinit', user], stdin_text=passwd)
    cmd = host.run_command('klist')
    print(cmd.stdout_text)


def qerun(host, command, stdin_text=None, exp_returncode=0, exp_output=None):
    """ utility function to run command on host and check output """
    cmd = host.run_command(command, stdin_text, raiseonerr=False)
    cmd.stdout_text.rstrip()

    print("RETURNCODE:----")
    print("GOT: ", cmd.returncode)
    print("EXPECTED: ", exp_returncode)
    if cmd.returncode != exp_returncode:
        pytest.xfail("returncode mismatch.")

    print("OUTPUT:--------")
    print("GOT: ", cmd.stdout_text)
    print("EXPECTED: ", exp_output)
    if exp_output is None:
        print("Not checking expected output")
    elif exp_output not in cmd.stdout_text:
        pytest.xfail("expected output not found")

    print("COMMAND SUCCEEDED!")


def qe_http_get(url):
    """ experimental function to get web page """
    import urllib2
    request = urllib2.urlopen(url)
    return request


def qe_http_krb_get(host, url, user, passwd):
    """ experimental function to get web page with kerb ticket """
    import requests
    import kerberos
    from urlparse import urlparse
    kinit_as_user(host, user, passwd)
    url_hostname = urlparse(url).hostname
    krb_context = kerberos.authGSSClientInit("HTTP@" + url_hostname)[1]
    try:
        kerberos.authGSSClientStep(krb_context, "")
        negotiate_details = kerberos.authGSSClientResponse(krb_context)
    except kerberos.GSSError:
        negotiate_details = ""
    headers = {"Authorization": "Negotiate " + negotiate_details}
    return requests.get(url, headers=headers).status_code


def ldapmodify_cmd(host, uri, username, password, ldif_file):
    """ ldapmodify command to support changes via ldif files """
    # host.qerun(['ldapmodify', '-H', uri, '-D', username, '-w',
    #              password, '-f', ldif_file])
    host.qerun(['yum', '--nogpgcheck', '-y', 'install', 'strace'])
    host.qerun(['strace', '-vtfo', '/tmp/ldapmodify.strace',
                'ldapmodify', '-H', uri, '-D', username, '-w', password,
                '-f', ldif_file])


def ldapmodify_py(uri, username, password, ldif_file):
    """ ldapmodify command to support changes via ldif files """
    import ldif
    import ldap
    import ldap.modlist as modlist
    ldapobj = ldap.initialize(uri)
    ldapobj.simple_bind_s(username, password)
    time.sleep(5)
    lfile = open(ldif_file)
    last_dn = ''
    parser = ldif.LDIFRecordList(lfile)
    parser.parse()
    for dn, entry in parser.all_records:
        ml = []
        if dn is None:
            dn = last_dn
        if 'replace' in entry.keys():
            ml = [(ldap.MOD_REPLACE, entry['replace'][0],
                   entry[entry['replace'][0]])]
            ldapobj.modify_s(dn, ml)
        else:
            ml = modlist.addModlist(entry)
            ldapobj.add_s(dn, ml)
        last_dn = dn
    lfile.close()
    ldapobj.unbind()


def service_control(host, service, function):
    """ wrapper to handle different service management systems """
    if '@' in service:
        service_file = service.split('@')[0] + '@'
    else:
        service_file = service

    if host.transport.file_exists(paths.SYSTEMD_DIR + service_file +
                                  '.service'):
        if function is 'on' or function is 'off':
            function = re.sub('off', 'disable', function)
            function = re.sub('on', 'enable', function)
        service_cmd = ['systemctl', function, service]
    else:
        service = service.split('@')[0]
        if 'off' in function or 'on' in function:
            service_cmd = ['chkconfig', service, function]
        else:
            service_cmd = ['service', service, function]

    print("service_control Running: [%s]" % " ".join(service_cmd))
    cmd = host.run_command(service_cmd, raiseonerr=False)
    if cmd.stdout_text:
        print("service_control STDOUT: %s " % cmd.stdout_text)
    if cmd.stderr_text:
        print("service_control STDERR: %s " % cmd.stderr_text)

    return cmd


def run_pk12util(host, args):
    """
    Helper function to run pk12util
    """
    new_args = [paths.PK12UTIL]
    args = new_args + args
    args = " ".join(args)
    print("Running pk12util command : %s " % args)
    return host.run_command(args, raiseonerr=False)


def create_noise_file():
    """
    Helper function to create a file with random content.
    This file is required for functions like certutil and pk12util
    """
    # Create noise
    noise = array.array('B', os.urandom(128))
    (noise_fd, noise_name) = tempfile.mkstemp()
    os.write(noise_fd, noise)
    os.close(noise_fd)
    return noise_name


def disable_dnssec(host):
    """Disable's DNSSEC and restart named-pkcs11 service"""
    namedcfg = '/etc/named.conf'
    namedtxt = host.get_file_contents(namedcfg)
    namedtxt = re.sub('dnssec-validation yes',
                      'dnssec-validation no',
                      namedtxt)
    host.put_file_contents(namedcfg, namedtxt)
    service_control(host, 'named-pkcs11', 'restart')


def dnsforwardzone_add(host, forwardzone, forwarder):
    """Add forwardzone for AD domain"""
    host.run_command('ipa dnsforwardzone-add ' + forwardzone +
                     ' --forwarder=' + forwarder +
                     ' --forward-policy=only', raiseonerr=False)
    service_control(host, 'named-pkcs11', 'restart')


def add_dnsforwarder(host, domain, ip):
    """Add DNS forwarder on AD machine for IPA domain"""

    cmd = host.run_command('dnscmd /ZoneInfo ' + domain, raiseonerr=False)
    if cmd.returncode == 1:
        cmd = host.run_command(['dnscmd', '/ZoneDelete', domain],
                               stdin_text='y', raiseonerr=False)
    cmd = host.run_command('dnscmd /zoneadd ' + domain + ' /forwarder ' + ip,
                           raiseonerr=False)
    cmd = host.run_command('ipconfig /flushdns', raiseonerr=False)
    cmd = host.run_command('dnscmd /clearcache', raiseonerr=False)


def ipa_config_mod(multihost, opts=None):
    """
    Helper function to modify ipa config
    """
    if opts and isinstance(opts, list):
        cmd = multihost.master.run_command(['ipa', 'config-mod'] + opts,
                                           raiseonerr=False)
        if cmd.returncode != 0:
            if 'no modifications to be performed' in cmd.stdout_text:
                return 1
            else:
                return 0
        else:
            return 0
    else:
        print("No operation performed")
        return 2


def setenforce(host, value):
    """ selinux setenforce command """
    host.run_command(['setenforce', value])


def get_domain_level(host):
    """
    Get the IPA Domain Level
    """
    try:
        host.kinit_as_admin()
        cmd = host.run_command(['ipa', 'domainlevel-get'], raiseonerr=False)
        found = re.search('Current domain level: (?P<level>.+)\n',
                          cmd.stdout_text, re.MULTILINE)
        domain_level = found.group('level')
    except StandardError as errval:
        print("Unable to run domainlevel-get command: %s" % errval)
        domain_level = 0
    return int(domain_level)


def ipa_version_gte(master, version):
    """
    Get IPA Version from Master and compare to version passed
    - if version passed is greater than or equal, True
    - if version passed is less than, False
    """
    cmd = master.run_command(['ipa-server-install', '--version'])
    ipa_version = cmd.stdout_text
    if StrictVersion(ipa_version) >= StrictVersion(version):
        return True
    else:
        return False


def sssd_cache_reset(host):
    """
    Helper function to reset the sssd cache
    :param host: hostname
    :return:
    """
    service_control(host, 'sssd', 'stop')
    host.run_command('rm -rf /var/lib/sss/db/*', set_env=True)
    host.run_command('rm -rf /var/lib/sss/mc/*', set_env=True)
    service_control(host, 'sssd', 'start')


def start_firewalld(host):
    """
    Helper function to start firewalld
    :param host: hostname
    :return:
    """
    print("Starting Firewalld")
    for i in ['enable', 'start']:
        service_control(host, 'firewalld', i)


def stop_firewalld(host):
    """
    Helper function to stop firewalld
    :param host: hostname
    :return:
    """
    print("Stopping Firewalld")
    for i in ['disable', 'stop']:
        service_control(host, 'firewalld', i)

def mkdtemp(host, tempdir=None):
    """
    Helper function to create a tempfile
    :param host: hostname
    :param tempdir: Temp directory name
    :return: directory name
    """
    if tempdir is None:
        tempdir = "/tmp/{0}".format(rand_str_generator())
    print("Creating temp directory {0}".format(tempdir))
    cmdstr = "mkdir {0}".format(tempdir)
    print("Executing: {0}".format(cmdstr))
    cmd = host.run_command(cmdstr, raiseonerr=False)
    if cmd.returncode == 0:
        return tempdir
    else:
        return ''

def rand_str_generator(size=6, chars=None):
    """
    Generate a random string
    """
    if chars is None:
        chars = string.ascii_uppercase + string.ascii_lowercase
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))

def chcon(host, context=None, dirname=None):
    """
    Helper function to change SELinux Context
    """
    cmdstr = "chcon -t {0} {1}".format(context, dirname)
    print("Executing: {0}".format(cmdstr))
    return host.run_command(cmdstr, raiseonerr=False)
