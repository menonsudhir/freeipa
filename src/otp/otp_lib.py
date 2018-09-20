'''
Helper functions required for auth-ident
'''
from ipa_pytests.shared.user_utils import add_ipa_user, find_ipa_user, \
                                          del_ipa_user
from ipa_pytests.shared.rpm_utils import check_rpm
from ipa_pytests.shared.utils import service_control
from ipa_pytests.shared import paths
import base64
import re
import time

RAD_USERS_LOCAL = '/tmp/users'


def add_user(multihost, user_to_create):
    """ add user """
    add_ipa_user(multihost.master,
                 user_to_create,
                 multihost.master.config.admin_pw)


def krb_destroy(host):
    """ krb destroy """
    host.run_command([
        'kdestroy', '-A'])


def otp_key_convert(key):
    """ convert base64 to base32 to oathtool can take it """
    decode = base64.b64decode(key)
    encode = base64.b32encode(decode)
    return encode.decode('utf-8')


def get_otp(multihost, otp_key):
    """ generate otp auth """
    output = multihost.master.run_command(
        [paths.OATHTOOL, "-b", str(otp_key), "--totp"])
    return output.stdout_text


def get_krb_cache(multihost, user, host=None):
    """ Get location of krb cache """
    if host is None:
        host = multihost.master
    host.kinit_as_admin()
    cmd = find_ipa_user(multihost.master, user)
    if cmd.returncode == 0:
        del_ipa_user(multihost.master, user)
    add_ipa_user(host,
                 user,
                 multihost.master.config.admin_pw)
    host.kinit_as_user(
        user, multihost.master.config.admin_pw)
    cmd = host.run_command([
        'klist'])
    print("STDOUT: ")
    print(cmd.stdout_text)
    print("STDERR: ")
    print(cmd.stderr_text)
    search = re.search('KCM.+(?!$)', cmd.stdout_text)
    return str(search.group())


def get_otp_key(text):
    """ parse otptoken-add and take key """
    search = re.search('(?<=Key: ).+(?!$)', text)
    return str(search.group())


def add_token(multihost, owner):
    """ generate otp token """
    cmd = multihost.master.run_command([
        'ipa', 'otptoken-add', '--type=totp',
        '--no-qrcode',
        '--owner=%s' % owner])
    return cmd.stdout_text


def prepare_radiusd(multihost, user):
    """ prepare radius server """
    check_rpm(multihost.client, ['freeradius', 'freeradius-ldap',
                                 'freeradius-utils', 'wpa_supplicant'])
    multihost.master.transport.get_file(paths.RAD_USERS, RAD_USERS_LOCAL)
    new = ''
    with open(RAD_USERS_LOCAL, 'r') as fin:
        new = user + " Cleartext-Password := \"" + \
               multihost.master.config.admin_pw + "\"\n"
        new += fin.read()
    with open(RAD_USERS_LOCAL, 'w') as fout:
        fout.write(new)
    multihost.master.transport.put_file(RAD_USERS_LOCAL, paths.RAD_USERS)
    service_control(multihost.master, 'radiusd', 'start')
    time.sleep(10)


def ssh_test(multihost, user, passwd=None):
    """ ssh test """
    if passwd is None:
        multihost.client.run_command([
            'ssh', user + '@' + multihost.master.hostname, 'hostname'
            ])
    else:
        multihost.client.run_command([
            'ssh', user + '@' + multihost.master.hostname, 'hostname'
            ], stdin_text=passwd)


def ssh_neg_test(multihost, user):
    """ negative ssh test """
    cmd = multihost.client.run_command([
        'ssh', user + '@' + multihost.master.hostname, 'hostname'
        ], raiseonerr=False)
    assert cmd.returncode != 0
