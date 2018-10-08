"""
Overview: IDView Testcase automation
"""

from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.shared.utils import (disable_dnssec, dnsforwardzone_add,
                                      add_dnsforwarder, sssd_cache_reset)
from ipa_pytests.qe_install import adtrust_install
from ipa_pytests.shared.rpm_utils import check_rpm
from ipa_pytests.shared.utils import kinit_as_user
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.utils import service_control
from ipa_pytests.shared.user_utils import *
from ipa_pytests.qe_install import setup_client, setup_master
from ipa_pytests.qe_install import adtrust_install, uninstall_client, uninstall_server


from ipa_pytests.shared.idviews_lib import *
import time
import pytest


class Testsubidview(object):
    """ Test Class """

    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        multihost.client = multihost.clients[0]
        print("MASTER: ", multihost.master.hostname)
        print("CLIENT: ", multihost.client.hostname)
        setup_master(multihost.master)
        setup_client(multihost.client, multihost.master)

        disable_dnssec(multihost.master)
        check_rpm(multihost.master, ['expect'])
        adtrust_install(multihost.master)

        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])
        domain = multihost.master.domain.name

        etchosts = '/etc/hosts'
        etchostscfg = multihost.master.get_file_contents(etchosts)
        etchostscfg += '\n' + ad1.ip + ' ' + ad1.hostname + '\n'
        multihost.master.put_file_contents(etchosts, etchostscfg)
        dnsforwardzone_add(multihost.master, forwardzone, ad1.ip)
        time.sleep(20)

        add_dnsforwarder(ad1, domain, multihost.master.ip)
        time.sleep(20)

        cmd = multihost.master.run_command('dig +short SRV _ldap._tcp.' +
                                           forwardzone, raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if ad1.hostname in cmd.stdout_text:
            print("dns resolution passed for ad domain")
        else:
            pytest.xfail("dns resolution failed for ad domain")
        cmd = multihost.master.run_command('dig +short SRV @' + ad1.ip +
                                           ' _ldap._tcp.' + domain,
                                           raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if domain in cmd.stdout_text:
            print("dns resolution passed for ipa domain")
        else:
            pytest.xfail("dns resolution failed for ipa domain")

        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])
        domain = multihost.master.domain.name
        realm = multihost.master.domain.realm
        multihost.master.kinit_as_admin()

    def test_activedir_password(self, multihost):
        """Adding trust with Windows AD"""
        multihost.master.kinit_as_admin()
        cmd = "ipa trust-add --two-way=true " + multihost.master.config.ad_top_domain + " --admin=" + \
              multihost.master.config.ad_user + " --password"
        with open('test1.exp', 'w') as f:
            f.write('set timeout 5\n')
            f.write('set force_conservative 0\n')
            f.write('set send_slow {1.1}\n')
            f.write('spawn %s\n' % (cmd))
            f.write('expect "Active Directory domain administrator\'\s password:"\n')
            f.write("send -s -- \"Secret123\\r\"\n")
            f.write('expect eof')
        multihost.master.transport.put_file('test1.exp', '/tmp/test1.exp')
        output = multihost.master.run_command(['expect', '/tmp/test1.exp'], raiseonerr=False)
        if output.returncode != 0:
            print(output.stderr_text)
        else:
            print(output.stdout_text)

    def test_useradd_subdomain(self, multihost):
        multihost.master.kinit_as_admin()
        check_rpm(multihost.master, ['adcli'])
        cmd = multihost.ads[0].run_command(['kinit',
                                            multihost.master.config.ad_user + '@' + multihost.master.config.ad_sub_domain],
                                           stdin_text=multihost.master.config.ad_pwd,
                                           raiseonerr=False)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        print(cmd.returncode)
        if cmd.returncode == 1:
            for i in range(30):
                cmd = multihost.master.run_command(['adcli', 'create-user',
                                                    '--domain=' + multihost.master.config.ad_sub_domain,
                                                   'idviewuser%s' % str(i), '-x'],
                                                   stdin_text=multihost.master.config.ad_pwd,
                                                   raiseonerr=False)

    def test_0002_sub_useradd(self, multihost):
        """Adding user to specific view"""
        sssd_cache_reset(multihost.master)
        time.sleep(20)
        cmd = idview_add(multihost.master, viewname='view')
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser1@' + multihost.master.config.ad_sub_domain],
                               exp_returncode=0,
                               exp_output='Added User ID override '
                                          '"idviewuser1@' + multihost.master.config.ad_sub_domain)

    def test_0003_sub_useradduid(self, multihost):
        """Trusted AD user is added to view  using uid option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser2@' + multihost.master.config.ad_sub_domain, '--uid=200000'],
                               exp_returncode=0,
                               exp_output='Added User ID override '
                                          '"idviewuser2@' + multihost.master.config.ad_sub_domain)

    def test_0004_sub_sameuidgid(self, multihost):
        """Trusted AD user is added to view  using uid, gidnumber option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser3@' + multihost.master.config.ad_sub_domain,
                                '--uid=200000', '--gidnumber=200000'], exp_returncode=0,
                               exp_output='Added User ID override '
                                          '"idviewuser3@' + multihost.master.config.ad_sub_domain)

    def test_0005_sub_iffuidgid(self, multihost):
        """Trusted AD user is added to view  using uid, gidnumber option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser4@' + multihost.master.config.ad_sub_domain,
                                '--uid=200000', '--gidnumber=200001'], exp_returncode=0,
                               exp_output='Added User ID override '
                                          '"idviewuser4@' + multihost.master.config.ad_sub_domain)

    def test_0006_sub_dduidlogin(self, multihost):
        """Trusted AD user is added to view  using uid, login option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser5@' + multihost.master.config.ad_sub_domain,
                                '--uid=30000', '--login=user5'],
                               exp_returncode=0, exp_output='User login: user5')

    def test_0007_sub_adduidgecos(self, multihost):
        """Trusted AD user is added to view  using uid, gecos option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser6@' + multihost.master.config.ad_sub_domain,
                                '--uid=30001', '--gecos=user6'],
                               exp_returncode=0, exp_output='GECOS: user6')

    def test_0008_sub_adduidhomedir(self, multihost):
        """Trusted AD user is added to view  using uid, homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser7@' + multihost.master.config.ad_sub_domain,
                                '--uid=30002', '--homedir=/home/user7'], exp_returncode=0,
                               exp_output='Home directory: /home/user7')

    def test_0009_sub_adduidshell(self, multihost):
        """Trusted AD user is added to view using uid shell option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser8@' + multihost.master.config.ad_sub_domain,
                                '--uid=30003', '--shell=/bin/sh'], exp_returncode=0,
                               exp_output='Login shell: /bin/sh')

    def test_0011_sub_adduiddesc(self, multihost):
        """Trusted AD user is added to view using uid and desc option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser10@' + multihost.master.config.ad_sub_domain,
                                '--uid=30005', '--desc=USER10'],
                               exp_returncode=0, exp_output='Description: USER10')

    def test_0012_sub_addgidnumber(self, multihost):
        """Trusted AD user is added to view using gid option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser11@' + multihost.master.config.ad_sub_domain,
                                '--gid=40001'], exp_returncode=0, exp_output='GID: 40001')

    def test_0013_sub_addgidnumberlogin(self, multihost):
        """Trusted AD user is added to view using gid and login option """
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser12@' + multihost.master.config.ad_sub_domain,
                                '--gid=40002', '--login=user12'], exp_returncode=0,
                               exp_output='User login: user12')

    def test_0014_sub_addgidgecos(self, multihost):
        """Trusted AD user is added to view using gid and gecos option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser13@' + multihost.master.config.ad_sub_domain,
                                '--gid=40003', '--gecos=gecostest'],
                               exp_returncode=0, exp_output='GECOS: gecostest')

    def test_0015_sub_addgidgecoshomedir(self, multihost):
        """Trusted AD user is added to view using gid and homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser14@' + multihost.master.config.ad_sub_domain,
                                '--gid=40004', '--homedir=/home/user14'],
                               exp_returncode=0, exp_output='Home directory: /home/user14')

    def test_0016_sub_addgidshell(self, multihost):
        """Trusted AD user is added to view using shell and gid option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser15@' + multihost.master.config.ad_sub_domain,
                                '--gid=40005', '--shell=/bin/sh'],
                               exp_returncode=0, exp_output='Login shell: /bin/sh')

    def test_0018_sub_addlogin(self, multihost):
        """Trusted AD user  is added to view along with --login option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser17@' + multihost.master.config.ad_sub_domain,
                                '--login=user17'], exp_returncode=0,
                               exp_output='User login: user17')

    def test_0019_sub_logingecos(self, multihost):
        """Trusted AD user  is added to view along with  login and gecos option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain,
                                '--login=user18', '--gecos=valid user'], exp_returncode=0,
                               exp_output='GECOS: valid user')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain],
                               exp_returncode=0)

    def test_0020_sub_loginhomedir(self, multihost):
        """Trusted AD user is added to view along with login and homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain,
                                '--login=user18', '--homedir=/home/test'], exp_returncode=0,
                               exp_output='Home directory: /home/test')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain],
                               exp_returncode=0)

    def test_0021_sub_loginshell(self, multihost):
        """
        Trusted AD user is added to view along with login and shell option
        """
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain,
                                '--login=user18', '--shell=/bin/sh'], exp_returncode=0,
                               exp_output='Login shell: /bin/sh')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain],
                               exp_returncode=0)

    def test_0023_sub_addgecos(self, multihost):
        """Trusted AD user is added to view along with gecos option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain,
                                '--gecos=user18'], exp_returncode=0,
                               exp_output='GECOS: user18')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain],
                               exp_returncode=0)

    def test_0024_sub_addgecoshomedir(self, multihost):
        """Trusted AD user is added to view along with gecos and homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain,
                                '--gecos="user18"', '--homedir=/home/test'], exp_returncode=0,
                               exp_output='Home directory: /home/test')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain],
                               exp_returncode=0)

    def test_0025_sub_addgecosshell(self, multihost):
        """Trusted AD user is added to view along with gecos and shell option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain,
                                '--gecos="user18"', '--shell=/bin/bash'], exp_returncode=0,
                               exp_output='Login shell: /bin/bash')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain],
                               exp_returncode=0)

    def test_0027_sub_addhomedir(self, multihost):
        """Trusted AD user is added to view with homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain,
                                '--homedir=/home/test'], exp_returncode=0,
                               exp_output='Home directory: /home/test')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain],
                               exp_returncode=0)

    def test_0028_sub_homedirshell(self, multihost):
        """Trusted AD user is added to view with homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain,
                                '--homedir=/home/test'], exp_returncode=0,
                               exp_output='Home directory: /home/test')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain],
                               exp_returncode=0)

    def test_0030_sub_addshell(self, multihost):
        """Trusted AD user is added to view with shell option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain,
                                '--shell=/bin/sh'], exp_returncode=0,
                               exp_output='Login shell: /bin/sh')

    def test_0036_sub_moddesc(self, multihost):
        """Trusted AD user in view is modified with desc option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain,
                                '--desc=desc1'], exp_returncode=0,
                               exp_output='Description: desc1')

    def test_0037_sub_modlogin(self, multihost):
        """Trusted AD user in view is modified with login option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain,
                                '--login=moduser1'], exp_returncode=0,
                               exp_output='User login: moduser1')

    def test_0038_sub_moduid(self, multihost):
        """Trusted AD user in view is modified with uid option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain,
                                '--uid=55555'], exp_returncode=0,
                               exp_output='UID: 55555')

    def test_0039_sub_modgecos(self, multihost):
        """Trusted AD user in view is modified with gecos option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain,
                                '--gecos=User18'], exp_returncode=0,
                               exp_output='GECOS: User18')

    def test_0040_sub_modgidnumber(self, multihost):
        """Trusted AD user in view is modified with gidnumber option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain,
                                '--gidnumber=777777'], exp_returncode=0,
                               exp_output='GID: 777777')

    def test_0041_sub_modhomedir(self, multihost):
        """Trusted AD user in view is modified with homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain,
                                '--homedir=/home/user18'], exp_returncode=0,
                               exp_output='Home directory: /home/user18')

    def test_0042_sub_modshell(self, multihost):
        """Trusted AD user in view is modified with shell option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view',
                                'idviewuser1@' + multihost.master.config.ad_sub_domain,
                                '--shell=/bin/sh'], exp_returncode=0,
                               exp_output='Login shell: /bin/sh')

    def test_0064_sub_showall(self, multihost):
        """Finding trusted AD user in view using show all option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-show', 'view',
                                'idviewuser1@' + multihost.master.config.ad_sub_domain, '--all'],
                               exp_returncode=0,
                               exp_output='objectclass: ')

    def test_0065_sub_showraw(self, multihost):
        """Finding trusted AD user in view using show raw option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-show', 'view',
                                'idviewuser1@' + multihost.master.config.ad_sub_domain, '--raw'],
                               exp_returncode=0,
                               exp_output='ipaanchoruuid: :SID:')

    def test_0066_sub_showall(self, multihost):
        """Finding trusted AD user in view using show all raw option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-show', 'view',
                                'idviewuser1@' + multihost.master.config.ad_sub_domain, '--all'],
                               exp_returncode=0,
                               exp_output='dn: ipaanchoruuid=')

    def test_0069_sub_idoverridedel(self, multihost):
        """Deleting a idoverride user from the view"""
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_sub_domain],
                               exp_returncode=0)

    def test_0010_sub_idoverride_uid_sshpubkey(self, multihost):
        """Adding a user with uid and pubkey"""
        multihost.master.kinit_as_admin()
        uid = '899989'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKS' \
              'rFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI9' \
              '6szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2W' \
              'IkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser21@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser21@' + multihost.master.config.ad_sub_domain,
                                '--sshpubkey=%s' %key,
                                '--uid=%s' %uid],
                               exp_returncode=0)

    def test_0017_sub_idoverride_gid_sshpubkey(self, multihost):
        """Adding a user with gidnumber and pubkey"""
        multihost.master.kinit_as_admin()
        gid = '899989'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKS' \
              'rFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI9' \
              '6szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2W' \
              'IkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser22@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser22@' + multihost.master.config.ad_sub_domain,
                                '--sshpubkey''=' + key,
                                '--gidnumber''=' + gid],
                               exp_returncode=0)

    def test_0022_sub_idoverride_login_sshpubkey(self, multihost):
        """Adding a user with login and pubkey"""
        multihost.master.kinit_as_admin()
        login = 'user23'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBK' \
              'SrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFA' \
              'I96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfk' \
              'u2WIkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== ' \
              'idviewuser23@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser23@' + multihost.master.config.ad_sub_domain,
                                '--sshpubkey''=' + key,
                                '--login''=' + login],
                               exp_returncode=0)

    def test_0026_sub_idoverride_gecos_sshpubkey(self, multihost):
        """Adding a user with gecos and pubkey"""
        multihost.master.kinit_as_admin()
        gecos = 'testuser'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKSrF' \
              'xSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szA' \
              'Vfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE1qo' \
              '4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser24@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser24@' + multihost.master.config.ad_sub_domain,
                                '--sshpubkey''=' + key,
                                '--gecos''=' + gecos],
                               exp_returncode=0)

    def test_0031_sub_idoverride_shell_sshpubkey(self, multihost):
        """Adding a user with gecos and pubkey"""
        multihost.master.kinit_as_admin()
        shell = '/bin/bash'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKSr' \
              'FxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96s' \
              'zAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE' \
              '1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser25@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser25@' + multihost.master.config.ad_sub_domain,
                                '--sshpubkey''=' + key,
                                '--homedir''=' + shell],
                               exp_returncode=0)

    def test_0029_sub_idoverride_homedir_sshpubkey(self, multihost):
        """Adding a user with gecos and pubkey"""
        multihost.master.kinit_as_admin()
        homedir = '/home/ipaaduser'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKSr' \
              'FxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96s' \
              'zAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE' \
              '1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser26@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser26@' + multihost.master.config.ad_sub_domain,
                                '--sshpubkey''=' + key,
                                '--homedir''=' + homedir],
                               exp_returncode=0)

    def test_0043_sub_idoverrideuser_mod_sshpubkey(self, multihost):
        """modifying a user pubkey"""
        multihost.master.kinit_as_admin()
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKS' \
              'rFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI9' \
              '6szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2W' \
              'IkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser26@modified'
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view',
                                'idviewuser26@' + multihost.master.config.ad_sub_domain,
                                '--sshpubkey''=' + key],
                               exp_returncode=0)

    def test_0048_sub_overridefind_anchor(self, multihost):
        """idoverride find using anchor """
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'idoverrideuser-find', 'view',
                                '--anchor=idviewuser25@' + multihost.master.config.ad_sub_domain],
                               exp_returncode=0,
                               exp_output='1 User ID overrides matched')

    def test_userdel_subdomain(self, multihost):
        multihost.master.kinit_as_admin()
        check_rpm(multihost.master, ['adcli'])
        cmd = multihost.ads[0].run_command(['kinit',
                                            multihost.master.config.ad_user + '@' + multihost.master.config.ad_sub_domain],
                                           stdin_text=multihost.master.config.ad_pwd,
                                           raiseonerr=False)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        print(cmd.returncode)
        if cmd.returncode == 1:
            for i in range(30):
                cmd = multihost.master.run_command(['adcli', 'delete-user',
                                                    '--domain=' + multihost.master.config.ad_sub_domain,
                                                    'idviewuser%s' % str(i), '-x'],
                                                   stdin_text=multihost.master.config.ad_pwd,
                                                   raiseonerr=False)
    def class_teardown(self, multihost):
        cmd = multihost.master.qerun('ipa trust-del ' + multihost.master.config.ad_top_domain)
        uninstall_client(multihost.client)
        uninstall_server(multihost.master)
