""" Functional Services Support Functions """
import re
import time
import ldap
import ldap.sasl


def curl_check(host, url):
    """ support function to check http access with curl command """
    cmd = host.run_command(['curl', '-v', '--negotiate', '-u:', url])
    return cmd.stdout_text


def ldap_sasl_check_positive(host, uri):
    """ support function to check ldap access for success """
    search = ['ldapsearch', '-H', uri, '-Y', 'GSSAPI', '-s', 'sub', '-b',
              'uid=ldapuser1,o=sasl.com', '(uid=*)', 'dn']
    host.run_command(search)


def ldap_sasl_check_positive_py(uri):
    """ support function to check ldap access for success native python """
    ldapobj = ldap.ldapobject.ReconnectLDAPObject(uri, trace_level=1,
                                                  trace_stack_limit=10,
                                                  retry_max=10)
    ldapobj.set_option(ldap.OPT_X_TLS_DEMAND, True)
    auth = ldap.sasl.gssapi('')
    try:
        ldapobj.sasl_interactive_bind_s('ldapuser1', auth)
    except Exception:
        raise ValueError('[Fail]: sasl bind failed')


def ldap_sasl_check_negative(host, uri, expected_message):
    """ support function to check ldap access for denial """
    search = ['ldapsearch', '-H', uri, '-Y', 'GSSAPI', '-s', 'sub', '-b',
              'uid=ldapuser1,o=sasl.com', '(uid=*)', 'dn']
    cmd = host.run_command(search, raiseonerr=False)
    output = cmd.stdout_text
    output += cmd.stderr_text
    if not re.search(expected_message, output):
        raise ValueError('[Fail]: sasl bind did not fail as expected')
    else:
        print("Failed as expected: \n%s" % output)


def ldap_sasl_check_negative_py(uri, expected_message):
    """ support function to check ldap access for denial native python """
    # ldapobj = ldap.initialize(uri)
    ldapobj = ldap.ldapobject.ReconnectLDAPObject(uri, trace_level=1,
                                                  trace_stack_limit=10,
                                                  retry_max=10)
    ldapobj.set_option(ldap.OPT_X_TLS_DEMAND, True)
    auth = ldap.sasl.gssapi('')
    try:
        ldapobj.sasl_interactive_bind_s('ldapuser1', auth)
    except ldap.LOCAL_ERROR as errval:
        if not re.search(expected_message, errval.args[0]['info']):
            print("ERROR: ", errval.args[0]['info'])
            raise ValueError('[Fail]: sasl bind did not fail as expected')
    else:
        raise ValueError('[Fail]: sasl bind passed when it should fail')


def ldap_simple_bind_check_positve(host, uri, username, password):
    """ support function to check simple ldap bind """
    search = ['ldapsearch', '-x', '-H', uri, '-D', username, '-w', password, '-b',
              'uid=ldapuser1,o=sasl.com', '(uid=*)', 'dn']
    host.run_command(search)


def ldap_simple_bind_check_py(uri, username, password):
    """ support function to check simple ldap bind native python """
    # ldapobj = ldap.initialize(uri)
    ldapobj = ldap.ldapobject.ReconnectLDAPObject(uri, trace_level=1,
                                                  trace_stack_limit=10,
                                                  retry_max=10)
    try:
        ldapobj.simple_bind_s(username, password)
    except Exception:
        raise ValueError('[Fail]: unable to bind with user and password')


def check_revoked(host, cert_dir):
    """ support function to check if certificate is revoked """
    max_checks = 5
    if host.transport.file_exists('/usr/lib64/nss/unsupported-tools/ocspclnt'):
        ocspcmd = '/usr/lib64/nss/unsupported-tools/ocspclnt'
    else:
        ocspcmd = '/usr/lib/nss/unsupported-tools/ocspclnt'

    for _ in range(max_checks):
        cmd = host.run_command([ocspcmd, '-S', host.hostname, '-d', cert_dir])
        if 'Certificate has been revoked' in cmd.stdout_text:
            print("stdout: %s" % cmd.stdout_text)
            return
        else:
            print("There was an error.   Checking again to be sure")
            print("stdout: %s" % cmd.stdout_text)
            print("stderr: %s" % cmd.stderr_text)
        time.sleep(2)

    host.run_command(['journalctl', '-xel'])
    raise ValueError('Certificate not revoked or unable to check')


def is_redundant_ca_dns_supported(host, service):
    """ support function to test if ipa-ca DNS name supported """
    host.kinit_as_admin()
    cmd = host.run_command(['ipa', 'service-show', '--all', '--raw', service])
    serial_number = re.search('serial_number: (.+?)\n', cmd.stdout_text).group(1)
    host.run_command(['ipa', 'cert-show', serial_number, '--out=/tmp/cert_to_check.crt'])
    cmd = host.run_command(['openssl', 'x509', '-text', '-in', '/tmp/cert_to_check.crt'])
    if re.search('OCSP.*URI.*http://ipa-ca', cmd.stdout_text):
        print("ipa-ca redundant dns URI found")
        return True
    else:
        print("ipa-ca redundant dns URI not found")
        return False


def wait_for_ldap(host, port):
    """ support function to wait to see if ldap is running """
    attempt = 1
    maxtries = 10
    search_string = ':' + str(port) + '.*LISTEN'
    while attempt <= maxtries:
        cmd = host.run_command(['netstat', '-an'])
        result = re.search(search_string, cmd.stdout_text)
        if result is None:
            print("LDAP does not appear to be running yet...waiting")
            time.sleep(60)
            attempt += 1
        else:
            break
