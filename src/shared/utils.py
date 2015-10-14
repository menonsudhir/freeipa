"""
Major shared support utility functions
- add_ipa_user - add user and set password
- kinit_as_uesr - kinit as user with password
- qerun - utility function to run command on host and check output
- qe_http_get - experimental function to get web page
- qe_http_krb_get - experimental function to get web page with kerb ticket
- ldapmodify - ldapmodify command
"""
import time
import pytest
import re


def add_ipa_user(host, user, passwd=None, first=None, last=None):
    """ Add an IPA user and set password """
    if passwd is None:
        passwd = "Secret123"
    if first is None:
        first = user
    if last is None:
        last = user
    chpass = 'Passw0rd1\n%s\n%s\n' % (passwd, passwd)
    print chpass
    host.kinit_as_admin()
    host.run_command(['ipa', 'user-add', "--first", first, "--last", last,
                      "--password", user], stdin_text="Passw0rd1")
    host.run_command(['kdestroy', '-A'])
    time.sleep(2)
    cmd = host.run_command(['kinit', user], stdin_text=chpass)
    print "PASSOUT: %s" % cmd.stdout_text
    print "PASSERR: %s" % cmd.stderr_text
    host.kinit_as_admin()


def kinit_as_user(host, user, passwd):
    """ Kinit as user with password """
    host.run_command('kdestroy -A')
    host.run_command(['kinit', user], stdin_text=passwd)
    cmd = host.run_command('klist')
    print cmd.stdout_text


def qerun(host, command, stdin_text=None, exp_returncode=0, exp_output=None):
    """ utility function to run command on host and check output """
    cmd = host.run_command(command, stdin_text, raiseonerr=False)
    cmd.stdout_text.rstrip()

    print "RETURNCODE:----"
    print "GOT: ", cmd.returncode
    print "EXPECTED: ", exp_returncode
    if cmd.returncode != exp_returncode:
        pytest.xfail("returncode mismatch.")

    print "OUTPUT:--------"
    print "GOT: ", cmd.stdout_text
    print "EXPECTED: ", exp_output
    if exp_output is None:
        print "Not checking expected output"
    elif exp_output not in cmd.stdout_text:
        pytest.xfail("expected output not found")

    print "COMMAND SUCCEEDED!"


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
    # host.qerun(['ldapmodify', '-H', uri, '-D', username, '-w', password, '-f', ldif_file])
    host.qerun(['yum', '--nogpgcheck', '-y', 'install', 'strace'])
    host.qerun(['strace', '-vtfo', '/tmp/ldapmodify.strace', 'ldapmodify', '-H', uri,
                '-D', username, '-w', password, '-f', ldif_file])


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
            ml = [(ldap.MOD_REPLACE, entry['replace'][0], entry[entry['replace'][0]])]
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

    if host.transport.file_exists('/usr/lib/systemd/system/' + service_file + '.service'):
        if function is 'on' or function is 'off':
            function = re.sub('off', 'disable', function)
            function = re.sub('on', 'enable', function)
        service_cmd = ['systemctl', function, service]
    else:
        if 'off' in function or 'on' in function:
            service_cmd = ['chkconfig', service, function]
        else:
            service_cmd = ['service', service, function]

    cmd = host.run_command(service_cmd, raiseonerr=False)
    return cmd


def list_rpms(host):
    """ list installed rpms """
    cmd = host.run_command(['rpm', '-qa', '--last'])
    rpmlog_file = "/var/log/rpm.list." + time.strftime('%H%M%S', time.localtime())
    print cmd.stdout_text
    print cmd.stderr_text
    host.put_file_contents(rpmlog_file, cmd.stdout_text)
