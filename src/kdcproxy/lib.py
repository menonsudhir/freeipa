'''
Helper functions required for test_kdcproxy
'''
import re
import pytest
from ipa_pytests.shared.utils import service_control


def update_krbv_conf(multihost, replica=False, httpanchor=None):
    '''
    Modify client's krb5.conf file using given parameters
    '''
    cfgget = '/etc/krb5.conf'
    cfgput = '/tmp/krb5.conf'
    multihost.client.qerun(['rm', '-rf', cfgput])
    krbvcfg = multihost.client.get_file_contents(cfgget)
    krbvcfg = re.sub('kdc = ' + multihost.master.hostname + ':88',
                     'kdc = https://' + multihost.master.hostname +
                     '/KdcProxy', krbvcfg)
    krbvcfg = re.sub('master_kdc = ' + multihost.master.hostname + ':88',
                     'master_kdc = https://' + multihost.master.hostname +
                     '/KdcProxy', krbvcfg)
    krbvcfg = re.sub('admin_server = ' + multihost.master.hostname +
                     ':749',
                     'admin_server = https://' + multihost.master.hostname +
                     '/KdcProxy', krbvcfg)
    krbvcfg = re.sub('kpasswd_server = ' + multihost.master.hostname +
                     ':464',
                     'kpasswd_server = https://' + multihost.master.hostname +
                     '/KdcProxy', krbvcfg)
    if replica:
        krbvcfg = re.sub('default_domain = ' + multihost.realm.lower(),
                         '\tkdc = https://' + multihost.replica.hostname +
                         '/KdcProxy\n\tadmin_server = https://' +
                         multihost.replica.hostname + '/KdcProxy\n' +
                         '\tkpasswd_server = https://' +
                         multihost.replica.hostname + '/KdcProxy\n' +
                         '\tdefault_domain = ' + multihost.realm.lower(),
                         krbvcfg)
    if httpanchor:
        krbvcfg = re.sub('default_domain = ' + multihost.realm.lower(),
                         'default_domain = ' + multihost.realm.lower() +
                         '\nhttp_anchors = ' + httpanchor, krbvcfg)

    multihost.client.put_file_contents(cfgput, krbvcfg)
    multihost.client.qerun(['mv', cfgget, cfgget + ".bak"],
                           exp_returncode=0)
    multihost.client.qerun(['cp', '-a', cfgput, cfgget],
                           exp_returncode=0)
    service_control(multihost.client, 'sssd', 'restart')


def revert_krbv_conf(multihost):
    '''
    Revert client's krb5.conf using backup file taken previously
    '''
    cfg = '/etc/krb5.conf'
    multihost.client.qerun(['mv', cfg + ".bak", cfg], exp_returncode=0)
    service_control(multihost.client, 'sssd', 'restart')


def pwpolicy_mod(multihost, args=None):
    '''
    Change IPA Global Password policy using parameters given
    '''
    multihost.master.kinit_as_admin()
    cmd = multihost.master.run_command(['ipa', 'pwpolicy-mod', args],
                                       raiseonerr=False)
    if cmd.returncode != 0:
        pytest.xfail("Failed to modify Password Policy with given parameter")


def change_user_passwd(multihost, username, password, exp_returncode=0):
    '''
    Change user password using kpasswd
    '''
    cmd = multihost.client.run_command(['kpasswd', username],
                                       stdin_text=password,
                                       raiseonerr=False)
    if cmd.returncode != exp_returncode:
        pytest.xfail("kpasswd %s failed expecting %d "
                     "got %d"
                     % (multihost.testuser, exp_returncode, cmd.returncode))
