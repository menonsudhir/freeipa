"""
Overview: IDView Testcase automation
"""

from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.shared.utils import (disable_dnssec, dnsforwardzone_add,
                                      add_dnsforwarder, sssd_cache_reset,
                                      service_control)
from ipa_pytests.shared.trust_utils import ipa_trust_add
from ipa_pytests.qe_install import adtrust_install, uninstall_server
from ipa_pytests.shared.rpm_utils import check_rpm
from ipa_pytests.shared.user_utils import *
from ipa_pytests.shared.idviews_lib import *
from ipa_pytests.qe_install import setup_master

import time

import pytest


def temp_workaround_bz_1659498(multihost):
    """ This is temporary workaround for BZ #1659498"""
    time.sleep(3)
    service_control(multihost.master, 'sssd', 'restart')
    cmd = multihost.master.run_command(['id',
                                        multihost.master.config.ad_user + '@' + multihost.master.config.ad_top_domain],
                                       raiseonerr=False)
    print(cmd.stdout_text)
    print(cmd.stderr_text)
    assert cmd.returncode == 0


class Testidview(object):
    """ Test Class """

    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)
        setup_master(multihost.master)

        disable_dnssec(multihost.master)
        check_rpm(multihost.master, ['expect'])
        adtrust_install(multihost.master)

        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.hostname.split(".")[1:])
        domain = multihost.master.domain.name

        etchosts = '/etc/hosts'
        etchostscfg = multihost.master.get_file_contents(etchosts)
        etchostscfg += '\n' + ad1.ip + ' ' + ad1.hostname + '\n'
        multihost.master.put_file_contents(etchosts, etchostscfg)

        dnsforwardzone_add(multihost.master, forwardzone, ad1.ip)

        add_dnsforwarder(ad1, domain, multihost.master.ip)

        cmd = multihost.master.run_command('dig +short SRV _ldap._tcp.' +
                                           forwardzone, raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if ad1.hostname in cmd.stdout_text:
            print("dns resolution passed for ad domain")
        else:
            pytest.fail("dns resolution failed for ad domain")
        cmd = multihost.master.run_command('dig +short SRV @' + ad1.ip +
                                           ' _ldap._tcp.' + domain,
                                           raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if domain in cmd.stdout_text:
            print("dns resolution passed for ipa domain")
        else:
            pytest.fail("dns resolution failed for ipa domain")

        multihost.master.kinit_as_admin()

    def test_activedir_password(self, multihost):
        """Adding trust with Windows AD"""
        multihost.master.kinit_as_admin()

        res = ipa_trust_add(
            host=multihost.master,
            addomain=multihost.master.config.ad_top_domain,
            login=multihost.master.config.ad_user,
            options_list=['--two-way=true', '--password'],
            stdin_text=multihost.master.config.ad_pwd,
            raiseonerr=True,
            retry_on_failure=True
        )
        if res.returncode != 0:
            print(res.stdout_text)
            print(res.stderr)
            pytest.fail('Establishing trust failed')

    def test_useradd_domain(self, multihost):
        multihost.master.kinit_as_admin()
        check_rpm(multihost.master, ['adcli'])

        for i in range(30):
            multihost.master.run_command(['adcli', 'create-user',
                                                '--domain=' + multihost.master.config.ad_top_domain,
                                                'idviewuser%s' % str(i)],
                                               stdin_text=multihost.master.config.ad_pwd,
                                               raiseonerr=False)

        sssd_cache_reset(multihost.master)
        temp_workaround_bz_1659498(multihost)

    def test_groupadd_domain(self, multihost):
        multihost.master.kinit_as_admin()
        check_rpm(multihost.master, ['adcli'])
        for i in range(20):
            multihost.master.run_command(['adcli', 'create-group',
                                                '--domain=' + multihost.master.config.ad_top_domain,
                                                'idviewgroup%s' % str(i)],
                                               stdin_text=multihost.master.config.ad_pwd,
                                               raiseonerr=False)
        sssd_cache_reset(multihost.master)
        temp_workaround_bz_1659498(multihost)


    def test_0070_addinteractively(self, multihost):
        """Interactively add  IDview on IPA server"""
        cmd = 'ipa idview-add'
        with open('test2.exp', 'w') as f:
            f.write('set force_conservative 0\n')
            f.write('set send_slow {1.1}\n')
            f.write('spawn %s\n' % (cmd))
            f.write('expect "ID View Name:"\n')
            f.write("send -s -- \"testview\\r\"\n")
            f.write('expect eof')
        multihost.master.transport.put_file('test2.exp', '/tmp/test2.exp')
        output = multihost.master.run_command(['expect', '/tmp/test2.exp'],
                                              raiseonerr=False)
        if output.returncode != 0:
            print(output.stderr_text)
        else:
            print(output.stdout_text)

    def test_0071_addwithoutoptions(self, multihost):
        """Adding view using idview-add command"""
        multihost.master.kinit_as_admin()
        cmd = idview_add(multihost.master, viewname='TestView2')
        print(cmd.stdout_text)
        assert 'Added ID View "TestView2"' in cmd.stdout_text

    def test_0072_adddescription(self, multihost):
        """Adding view using idview-add command and desc option"""
        cmd = idview_add(multihost.master, viewname='TestView6', desc='view6')
        print(cmd.stdout_text)
        assert 'Description: view6' in cmd.stdout_text

    def test_0073_addsameviewagain(self, multihost):
        """Adding view which already exists"""
        cmd = idview_add(multihost.master, viewname='TestView6', desc='view6')
        print(cmd.stdout_text)
        assert 'ipa: ERROR: ID View with name "TestView6" already exists' in cmd.stderr_text

    def test_0074_differentcase(self, multihost):
        """Adding view which already exists but with differentcase"""
        cmd = idview_add(multihost.master, viewname='TESTVIEW6', desc='view6')
        print(cmd.stdout_text)
        assert 'ipa: ERROR: ID View with name "TESTVIEW6" already exists' in cmd.stderr_text

    def test_0090_findname(self, multihost):
        """Find a specific view using idview-find command"""
        cmd = idview_find(multihost.master, viewname='TestView6')
        print(cmd.stdout_text)
        assert 'Number of entries returned 1' in cmd.stdout_text

    def test_0091_finddesc(self, multihost):
        """Find a specific view using  desc option"""
        cmd = idview_find(multihost.master, viewname='TestView6', desc='view6')
        print(cmd.stdout_text)
        assert 'Number of entries returned 1' in cmd.stdout_text

    def test_0092_findall(self, multihost):
        """Find all views on the IPA  box"""
        cmd = idview_find(multihost.master, alloption='all')
        print(cmd.stdout_text)
        assert '4 ID Views matched' in cmd.stdout_text

    def test_0093_findraw(self, multihost):
        """find view with raw option"""
        cmd = idview_find(multihost.master, raw='raw')
        print(cmd.stdout_text)
        assert '4 ID Views matched' in cmd.stdout_text

    def test_0094_findallraw(self, multihost):
        """Find views using all and raw option"""
        cmd = idview_find(multihost.master, allraw='allraw')
        print(cmd.stdout_text)
        assert '4 ID Views matched' in cmd.stdout_text

    def test_0095_findsizelimit(self, multihost):
        """Find idview with specified sizelimit """
        cmd = idview_find(multihost.master, sizelimit='2')
        print(cmd.stdout_text)
        assert '2 ID Views matched' in cmd.stdout_text

    def test_0096_findcaseinsensitive(self, multihost):
        """Find idview  as case insensitive option"""
        cmd = idview_find(multihost.master, viewname='TESTVIEW2')
        print(cmd.stdout_text)
        assert '1 ID View matched' in cmd.stdout_text

    def test_0098_modrename(self, multihost):
        """Renaming idviews using rename option"""
        multihost.master.qerun(
            ['ipa', 'idview-mod', 'testview', '--rename=view'],
            exp_returncode=0, exp_output='ID View Name: view')

    def test_0099_moddescription(self, multihost):
        """Modify idview using desc  option"""
        multihost.master.qerun(
            ['ipa', 'idview-mod', 'testview2', '--desc=view2'],
            exp_returncode=0, exp_output='Description: view2')

    def test_0100_moddefaulttrust(self, multihost):
        """Modify default trust view """
        multihost.master.qerun(['ipa', 'idview-mod', 'default trust view'],
                               exp_returncode=1,
                               exp_output='ipa: ERROR: ID View Default Trust View cannot be '
                                          'deleted/modified: system ID View')

    def test_0002_useradd(self, multihost):
        """Adding user to specific view"""
        sssd_cache_reset(multihost.master)
        temp_workaround_bz_1659498(multihost)
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser1@' + multihost.master.config.ad_top_domain],
                               exp_returncode=0,
                               exp_output='Added User ID override '
                                          '"idviewuser1@' + multihost.master.config.ad_top_domain)

    def test_0003_useradduid(self, multihost):
        """Trusted AD user is added to view  using uid option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser2@' + multihost.master.config.ad_top_domain,
                                '--uid=200000'],
                               exp_returncode=0,
                               exp_output='Added User ID override '
                                          '"idviewuser2@' + multihost.master.config.ad_top_domain)

    def test_0004_sameuidgid(self, multihost):
        """Trusted AD user is added to view  using uid, gidnumber option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser3@' + multihost.master.config.ad_top_domain,
                                '--uid=200000', '--gidnumber=200000'],
                               exp_returncode=0,
                               exp_output='Added User ID override '
                                          '"idviewuser3@' + multihost.master.config.ad_top_domain)

    def test_0005_diffuidgid(self, multihost):
        """Trusted AD user is added to view  using uid, gidnumber option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser4@' + multihost.master.config.ad_top_domain,
                                '--uid=200000', '--gidnumber=200001'],
                               exp_returncode=0,
                               exp_output='Added User ID override '
                                          '"idviewuser4@' + multihost.master.config.ad_top_domain)

    def test_0006_adduidlogin(self, multihost):
        """Trusted AD user is added to view  using uid, login option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser5@' + multihost.master.config.ad_top_domain,
                                '--uid=30000', '--login=user5'],
                               exp_returncode=0,
                               exp_output='User login: user5')

    def test_0007_adduidgecos(self, multihost):
        """Trusted AD user is added to view  using uid, gecos option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser6@' + multihost.master.config.ad_top_domain,
                                '--uid=30001', '--gecos=user6'],
                               exp_returncode=0, exp_output='GECOS: user6')

    def test_0008_adduidhomedir(self, multihost):
        """Trusted AD user is added to view  using uid, homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser7@' + multihost.master.config.ad_top_domain,
                                '--uid=30002', '--homedir=/home/user7'],
                               exp_returncode=0,
                               exp_output='Home directory: /home/user7')

    def test_0009_adduidshell(self, multihost):
        """Trusted AD user is added to view using uid shell option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser8@' + multihost.master.config.ad_top_domain,
                                '--uid=30003', '--shell=/bin/sh'],
                               exp_returncode=0,
                               exp_output='Login shell: /bin/sh')

    def test_0011_adduiddesc(self, multihost):
        """Trusted AD user is added to view using uid and desc option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser10@' + multihost.master.config.ad_top_domain,
                                '--uid=30005', '--desc=USER10'],
                               exp_returncode=0,
                               exp_output='Description: USER10')

    def test_0012_addgidnumber(self, multihost):
        """Trusted AD user is added to view using gid option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser11@' + multihost.master.config.ad_top_domain,
                                '--gid=40001'], exp_returncode=0,
                               exp_output='GID: 40001')

    def test_0013_addgidnumberlogin(self, multihost):
        """Trusted AD user is added to view using gid and login option """
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser12@' + multihost.master.config.ad_top_domain,
                                '--gid=40002', '--login=user12'],
                               exp_returncode=0,
                               exp_output='User login: user12')

    def test_0014_addgidgecos(self, multihost):
        """Trusted AD user is added to view using gid and gecos option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser13@' + multihost.master.config.ad_top_domain,
                                '--gid=40003', '--gecos=gecostest'],
                               exp_returncode=0, exp_output='GECOS: gecostest')

    def test_0015_addgidgecoshomedir(self, multihost):
        """Trusted AD user is added to view using gid and homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser14@' + multihost.master.config.ad_top_domain,
                                '--gid=40004', '--homedir=/home/user14'],
                               exp_returncode=0,
                               exp_output='Home directory: /home/user14')

    def test_0016_addgidshell(self, multihost):
        """Trusted AD user is added to view using shell and gid option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser15@' + multihost.master.config.ad_top_domain,
                                '--gid=40005', '--shell=/bin/sh'],
                               exp_returncode=0,
                               exp_output='Login shell: /bin/sh')

    def test_0018_addlogin(self, multihost):
        """Trusted AD user  is added to view along with --login option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser17@' + multihost.master.config.ad_top_domain,
                                '--login=user17'], exp_returncode=0,
                               exp_output='User login: user17')

    def test_0019_logingecos(self, multihost):
        """Trusted AD user  is added to view along with  login and gecos option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain,
                                '--login=user18', '--gecos=valid user'],
                               exp_returncode=0,
                               exp_output='GECOS: valid user')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain],
                               exp_returncode=0)

    def test_0020_loginhomedir(self, multihost):
        """Trusted AD user is added to view along with login and homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain,
                                '--login=user18', '--homedir=/home/test'],
                               exp_returncode=0,
                               exp_output='Home directory: /home/test')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain],
                               exp_returncode=0)

    def test_0021_loginshell(self, multihost):
        """
        Trusted AD user is added to view along with login and shell option
        """
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain,
                                '--login=user18', '--shell=/bin/sh'],
                               exp_returncode=0,
                               exp_output='Login shell: /bin/sh')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain],
                               exp_returncode=0)

    def test_0023_addgecos(self, multihost):
        """Trusted AD user is added to view along with gecos option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain,
                                '--gecos=user18'], exp_returncode=0,
                               exp_output='GECOS: user18')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain],
                               exp_returncode=0)

    def test_0024_addgecoshomedir(self, multihost):
        """Trusted AD user is added to view along with gecos and homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain,
                                '--gecos="user18"', '--homedir=/home/test'],
                               exp_returncode=0,
                               exp_output='Home directory: /home/test')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain],
                               exp_returncode=0)

    def test_0025_addgecosshell(self, multihost):
        """Trusted AD user is added to view along with gecos and shell option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain,
                                '--gecos="user18"', '--shell=/bin/bash'],
                               exp_returncode=0,
                               exp_output='Login shell: /bin/bash')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain],
                               exp_returncode=0)

    def test_0027_addhomedir(self, multihost):
        """Trusted AD user is added to view with homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain,
                                '--homedir=/home/test'], exp_returncode=0,
                               exp_output='Home directory: /home/test')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain],
                               exp_returncode=0)

    def test_0028_homedirshell(self, multihost):
        """Trusted AD user is added to view with homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain,
                                '--homedir=/home/test'], exp_returncode=0,
                               exp_output='Home directory: /home/test')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain],
                               exp_returncode=0)

    def test_0030_addshell(self, multihost):
        """Trusted AD user is added to view with shell option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain,
                                '--shell=/bin/sh'], exp_returncode=0,
                               exp_output='Login shell: /bin/sh')

    def test_0036_moddesc(self, multihost):
        """Trusted AD user in view is modified with desc option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain,
                                '--desc=desc1'], exp_returncode=0,
                               exp_output='Description: desc1')

    def test_0037_modlogin(self, multihost):
        """Trusted AD user in view is modified with login option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain,
                                '--login=moduser1'], exp_returncode=0,
                               exp_output='User login: moduser1')

    def test_0038_moduid(self, multihost):
        """Trusted AD user in view is modified with uid option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain,
                                '--uid=55555'], exp_returncode=0,
                               exp_output='UID: 55555')

    def test_0039_modgecos(self, multihost):
        """Trusted AD user in view is modified with gecos option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain,
                                '--gecos=User18'], exp_returncode=0,
                               exp_output='GECOS: User18')

    def test_0040_modgidnumber(self, multihost):
        """Trusted AD user in view is modified with gidnumber option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain,
                                '--gidnumber=777777'], exp_returncode=0,
                               exp_output='GID: 777777')

    def test_0041_modhomedir(self, multihost):
        """Trusted AD user in view is modified with homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain,
                                '--homedir=/home/user18'], exp_returncode=0,
                               exp_output='Home directory: /home/user18')

    def test_0042_modshell(self, multihost):
        """Trusted AD user in view is modified with shell option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view',
                                'idviewuser1@' + multihost.master.config.ad_top_domain,
                                '--shell=/bin/sh'], exp_returncode=0,
                               exp_output='Login shell: /bin/sh')

    def test_0049_finddesc(self, multihost):
        """Finding trusted AD user in view using desc option"""
        multihost.master.qerun(
            ['ipa', 'idoverrideuser-find', 'view', '--desc=USER10'],
            exp_returncode=0,
            exp_output='Number of entries returned 1')

    def test_0050_findlogin(self, multihost):
        """Finding trusted AD user in view using login option"""
        multihost.master.qerun(
            ['ipa', 'idoverrideuser-find', 'view', '--login=user17'],
            exp_returncode=0,
            exp_output='Number of entries returned 1')

    def test_0051_finduid(self, multihost):
        """Finding trusted AD user in view using uid option"""
        multihost.master.qerun(
            ['ipa', 'idoverrideuser-find', 'view', '--uid=30005'],
            exp_returncode=0,
            exp_output='Number of entries returned 1')

    def test_0052_findgecos(self, multihost):
        """Finding trusted AD user in view using gecos option"""
        multihost.master.qerun(
            ['ipa', 'idoverrideuser-find', 'view', '--gecos=gecostest'],
            exp_returncode=0,
            exp_output='Number of entries returned 1')

    def test_0053_findgidnumber(self, multihost):
        """Finding trusted AD user in view using gidnumber option"""
        multihost.master.qerun(
            ['ipa', 'idoverrideuser-find', 'view', '--gidnumber=40001'],
            exp_returncode=0,
            exp_output='Number of entries returned 1')

    def test_0054_findhomedir(self, multihost):
        """Finding trusted AD user in view using homedir option"""
        multihost.master.qerun(
            ['ipa', 'idoverrideuser-find', 'view', '--homedir=/home/user7'],
            exp_returncode=0,
            exp_output='Number of entries returned 1')

    def test_0055_findshell(self, multihost):
        """Finding trusted AD user in view using shell option"""
        multihost.master.qerun(
            ['ipa', 'idoverrideuser-find', 'view', '--shell=/bin/sh'],
            exp_returncode=0,
            exp_output='Number of entries returned 4')

    def test_0056_findall(self, multihost):
        """Finding trusted AD user in view using all option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-find', 'view', '--all'],
                               exp_returncode=0)

    def test_0057_findraw(self, multihost):
        """Finding trusted AD user in view using raw option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-find', 'view', '--raw'],
                               exp_returncode=0,
                               exp_output='ipaanchoruuid: :SID: *')

    def test_0058_findallraw(self, multihost):
        """Find overriden user with all and raw options"""
        multihost.master.qerun(
            ['ipa', 'idoverrideuser-find', 'view', '--raw', '--all'],
            exp_returncode=0,
            exp_output='objectClass: *')

    def test_0059_findpkeyonly(self, multihost):
        """Find overridden user with --pkeyonly option"""
        multihost.master.qerun(
            ['ipa', 'idoverrideuser-find', 'view', '--pkey-only'],
            exp_returncode=0,
            exp_output='Number of entries returned *')

    def test_0064_showall(self, multihost):
        """Finding trusted AD user in view using show all option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-show', 'view',
                                'idviewuser1@' + multihost.master.config.ad_top_domain,
                                '--all'],
                               exp_returncode=0,
                               exp_output='objectclass: ')

    def test_0065_showraw(self, multihost):
        """Finding trusted AD user in view using show raw option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-show', 'view',
                                'idviewuser1@' + multihost.master.config.ad_top_domain,
                                '--raw'],
                               exp_returncode=0,
                               exp_output='ipaanchoruuid: :SID:')

    def test_0066_showall(self, multihost):
        """Finding trusted AD user in view using show all raw option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-show', 'view',
                                'idviewuser1@' + multihost.master.config.ad_top_domain,
                                '--all'],
                               exp_returncode=0,
                               exp_output='dn: ipaanchoruuid=')

    def test_0069_idoverridedel(self, multihost):
        """Deleting a idoverride user from the view"""
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view',
                                'idviewuser18@' + multihost.master.config.ad_top_domain],
                               exp_returncode=0)

    def test_0010_idoverride_uid_sshpubkey(self, multihost):
        """Adding a user with uid and pubkey"""
        multihost.master.kinit_as_admin()
        uid = '899989'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKS' \
              'rFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI9' \
              '6szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2W' \
              'IkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser21@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser21@' + multihost.master.config.ad_top_domain,
                                '--sshpubkey''=' + key,
                                '--uid''=' + uid],
                               exp_returncode=0)

    def test_0017_idoverride_gid_sshpubkey(self, multihost):
        """Adding a user with gidnumber and pubkey"""
        multihost.master.kinit_as_admin()
        gid = '899989'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKS' \
              'rFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI9' \
              '6szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2W' \
              'IkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser22@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser22@' + multihost.master.config.ad_top_domain,
                                '--sshpubkey''=' + key,
                                '--gidnumber''=' + gid],
                               exp_returncode=0)

    def test_0022_idoverride_login_sshpubkey(self, multihost):
        """Adding a user with login and pubkey"""
        multihost.master.kinit_as_admin()
        login = 'user23'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBK' \
              'SrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFA' \
              'I96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfk' \
              'u2WIkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== ' \
              'idviewuser23@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser23@' + multihost.master.config.ad_top_domain,
                                '--sshpubkey''=' + key,
                                '--login''=' + login],
                               exp_returncode=0)

    def test_0026_idoverride_gecos_sshpubkey(self, multihost):
        """Adding a user with gecos and pubkey"""
        multihost.master.kinit_as_admin()
        gecos = 'testuser'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKSrF' \
              'xSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szA' \
              'Vfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE1qo' \
              '4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser24@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser24@' + multihost.master.config.ad_top_domain,
                                '--sshpubkey''=' + key,
                                '--gecos''=' + gecos],
                               exp_returncode=0)

    def test_0031_idoverride_shell_sshpubkey(self, multihost):
        """Adding a user with gecos and pubkey"""
        multihost.master.kinit_as_admin()
        shell = '/bin/bash'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKSr' \
              'FxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96s' \
              'zAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE' \
              '1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser25@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser25@' + multihost.master.config.ad_top_domain,
                                '--sshpubkey''=' + key,
                                '--homedir''=' + shell],
                               exp_returncode=0)

    def test_0029_idoverride_homedir_sshpubkey(self, multihost):
        """Adding a user with gecos and pubkey"""
        multihost.master.kinit_as_admin()
        homedir = '/home/ipaaduser'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKSr' \
              'FxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96s' \
              'zAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE' \
              '1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser26@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view',
                                'idviewuser26@' + multihost.master.config.ad_top_domain,
                                '--sshpubkey''=' + key,
                                '--homedir''=' + homedir],
                               exp_returncode=0)

    def test_0043_idoverrideuser_mod_sshpubkey(self, multihost):
        """modifying a user pubkey"""
        multihost.master.kinit_as_admin()
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKS' \
              'rFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI9' \
              '6szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2W' \
              'IkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser26@modified'
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view',
                                'idviewuser26@' + multihost.master.config.ad_top_domain,
                                '--sshpubkey''=' + key],
                               exp_returncode=0)

    def test_0076_applydefaulttrustview(self, multihost):
        """Applying default trust view to a host"""
        hostname = 'hosts.testdomain.com'
        multihost.master.qerun(['ipa', 'idview-apply', 'default trust view',
                                '--hosts=' + hostname],
                               exp_returncode=1,
                               exp_output="ipa: ERROR: invalid 'ID View': Default Trust View cannot be "
                                          "applied on hosts")

    def test_0077_emptydeftrustview(self, multihost):
        """Applying default trust view with no value to host"""
        multihost.master.qerun(
            ['ipa', 'idview-apply', 'view', '--hosts=\" \"'],
            exp_returncode=1,
            exp_output='Number of hosts the ID View was applied to: 0')

    def test_0078_nonexistinghost(self, multihost):
        """Applying view to non existing host"""
        hostname = 'host.test123.com'
        multihost.master.qerun(
            ['ipa', 'idview-apply', 'view', '--hosts=' + hostname],
            exp_returncode=1,
            exp_output='hosts: host.test123.com: not found')

    def test_0079_nonexistingview(self, multihost):
        """Applying a non existing view"""
        hostname = 'host.test123.com'
        multihost.master.qerun(
            ['ipa', 'idview-apply', 'abc ', '--hosts=' + hostname],
            exp_returncode=2,
            exp_output='ipa: ERROR: no such entry')

    def test_0048_overridefind_anchor(self, multihost):
        """idoverride find using anchor """
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'idoverrideuser-find', 'view',
                                '--anchor=idviewuser25@' + multihost.master.config.ad_top_domain],
                               exp_returncode=0,
                               exp_output='1 User ID overrides? matched')

    def test_views_ipa_0001(self, multihost):
        """Adding user with uid option"""
        multihost.master.kinit_as_admin()
        user = 'vuser1'
        viewname = 'view1'
        uid = '77777'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd = idoverrideuser_add(multihost.master, viewname, user, uid)
        print(cmd.stdout_text)
        assert 'UID: 77777' in cmd.stdout_text

    def test_views_ipa_0002(self, multihost):
        """Adding user override with same uid and gid"""
        user = 'vuser2'
        viewname = 'view2'
        uid = '1234567'
        gid = '1234567'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd = idoverrideuser_add(multihost.master, viewname, user, uid, gid)
        print(cmd.stdout_text)
        assert 'UID: 1234567' in cmd.stdout_text
        assert 'GID: 1234567' in cmd.stdout_text

    def test_views_ipa_0003(self, multihost):
        """Adding user override with different uid and gid option"""
        user = 'vuser3'
        viewname = 'view3'
        uid = '1234567'
        gid = '1234568'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd = idoverrideuser_add(multihost.master, viewname, user, uid, gid)
        print(cmd.stdout_text)
        assert 'UID: 1234567' in cmd.stdout_text
        assert 'GID: 1234568' in cmd.stdout_text

    def test_views_ipa_0004(self, multihost):
        """Adding user override with uid and login options"""
        user = 'vuser4'
        viewname = 'view4'
        uid = '11111'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd = idoverrideuser_add(multihost.master, viewname='view4',
                                 user='vuser4', uid='11111', login='user4')
        print(cmd.stdout_text)
        assert 'User login: user4' in cmd.stdout_text
        assert 'UID: 11111' in cmd.stdout_text

    def test_views_ipa_0005(self, multihost):
        """Adding user override with uid and gecos options"""
        user = 'vuser5'
        viewname = 'view5'
        uid = '11112'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd = idoverrideuser_add(multihost.master, viewname='view5',
                                 user='vuser5', uid='11112', gecos='test5')
        print(cmd.stdout_text)
        assert 'GECOS: test5' in cmd.stdout_text
        assert 'UID: 11112' in cmd.stdout_text

    def test_views_ipa_0006(self, multihost):
        """Adding user override with uid and homedir options"""
        user = 'vuser6'
        viewname = 'view6'
        uid = '11113'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd = idoverrideuser_add(multihost.master, viewname='view6',
                                 user='vuser6', uid='11113',
                                 homedir='/home/test6')
        print(cmd.stdout_text)
        assert 'UID: 11113' in cmd.stdout_text
        assert 'Home directory: /home/test6' in cmd.stdout_text

    def test_views_ipa_0007(self, multihost):
        """Adding user override with uid and shell options"""
        user = 'vuser7'
        viewname = 'view7'
        uid = '11114'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd = idoverrideuser_add(multihost.master, viewname='view7',
                                 user='vuser7', uid='11114', shell='/bin/bash')
        print(cmd.stdout_text)
        assert 'UID: 11114' in cmd.stdout_text
        assert 'Login shell: /bin/bash' in cmd.stdout_text

    def test_views_ipa_0009(self, multihost):
        """Adding user override with uid and desc options"""
        user = 'vuser9'
        viewname = 'view9'
        uid = '11116'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd = idoverrideuser_add(multihost.master, viewname='view9',
                                 user='vuser9', uid='11116', desc='testing')
        print(cmd.stdout_text)
        assert 'UID: 11116' in cmd.stdout_text
        assert 'Description: testing' in cmd.stdout_text

    def test_views_ipa_0033(self, multihost):
        """Modifying user override description"""
        user = 'vuser10'
        viewname = 'view10'
        desc = 'changing desc'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd1 = idoverrideuser_add(multihost.master, viewname='view10',
                                  user='vuser10', desc='test')
        print(cmd1.stdout_text)
        assert 'Added User ID override "vuser10"' in cmd1.stdout_text
        cmd2 = idoverrideuser_mod(multihost.master, viewname, user,
                                  desc='changing desc')
        print(cmd2.stdout_text)
        assert 'Description: changing desc' in cmd2.stdout_text

    def test_views_ipa_0034(self, multihost):
        """Modifying user override login"""
        user = 'vuser11'
        viewname = 'view11'
        login = 'user11'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd1 = idoverrideuser_add(multihost.master, viewname='view11',
                                  user='vuser11', login='vuser')
        print(cmd1.stdout_text)
        assert 'Added User ID override "vuser11"' in cmd1.stdout_text
        cmd2 = idoverrideuser_mod(multihost.master, viewname, user,
                                  login='user11')
        print(cmd2.stdout_text)
        assert 'User login: user11' in cmd2.stdout_text

    def test_views_ipa_0035(self, multihost):
        """Modifying user override uid"""
        user = 'vuser12'
        viewname = 'view12'
        uid = '55555'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd1 = idoverrideuser_add(multihost.master, viewname='view12',
                                  user='vuser12', uid='77777')
        print(cmd1.stdout_text)
        assert 'Added User ID override "vuser12"' in cmd1.stdout_text
        cmd2 = idoverrideuser_mod(multihost.master, viewname, user, uid)
        print(cmd2.stdout_text)
        assert 'UID: 55555' in cmd2.stdout_text

    def test_views_ipa_0036(self, multihost):
        """Modifying user override gecos"""
        user = 'vuser13'
        viewname = 'view13'
        gecos = 'test'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd1 = idoverrideuser_add(multihost.master, viewname='view13',
                                  user='vuser13', gecos='test')
        print(cmd1.stdout_text)
        assert 'Added User ID override "vuser13"' in cmd1.stdout_text
        cmd2 = idoverrideuser_mod(multihost.master, viewname, user,
                                  gecos='testing gecos')
        print(cmd2.stdout_text)
        assert 'GECOS: testing gecos' in cmd2.stdout_text

    def test_views_ipa_0037(self, multihost):
        """Modifying user override gidnumber"""
        user = 'vuser14'
        viewname = 'view14'
        gidnumber = '88888'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd1 = idoverrideuser_add(multihost.master, viewname='view14',
                                  user='vuser14', gid='88888')
        print(cmd1.stdout_text)
        assert 'Added User ID override "vuser14"' in cmd1.stdout_text
        cmd2 = idoverrideuser_mod(multihost.master, viewname, user,
                                  gid='77777')
        print(cmd2.stdout_text)
        assert 'GID: 77777' in cmd2.stdout_text

    def test_views_ipa_0038(self, multihost):
        """Modifying user override homedir"""
        user = 'vuser15'
        viewname = 'view15'
        homedir = '/home/test15'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd1 = idoverrideuser_add(multihost.master, viewname='view15',
                                  user='vuser15', homedir='/home/test15')
        print(cmd1.stdout_text)
        assert 'Added User ID override "vuser15"' in cmd1.stdout_text
        cmd2 = idoverrideuser_mod(multihost.master, viewname,
                                  user, homedir='/home/vuser15')
        print(cmd2.stdout_text)
        assert 'Home directory: /home/vuser15' in cmd2.stdout_text

    def test_views_ipa_0039(self, multihost):
        """Modifying user override shell"""
        user = 'vuser16'
        viewname = 'view16'
        shell = '/bin/sh'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd1 = idoverrideuser_add(multihost.master, viewname='view16',
                                  user='vuser16', shell='/bin/sh')
        print(cmd1.stdout_text)
        assert 'Added User ID override "vuser16"' in cmd1.stdout_text
        cmd2 = idoverrideuser_mod(multihost.master, viewname,
                                  user, shell='/bin/bash')
        print(cmd2.stdout_text)
        assert 'Login shell: /bin/bash' in cmd2.stdout_text

    def test_views_ipa_0042(self, multihost):
        """Adding ipa group and adding group override"""
        groupname = 'ipagroup1'
        viewname = 'gview1'
        multihost.master.kinit_as_admin()
        add_ipa_group(multihost.master, groupname)
        idview_add(multihost.master, viewname)
        cmd = idoverridegroup_add(multihost.master, viewname, groupname)
        print(cmd.stdout_text)
        assert 'Added Group ID override "ipagroup1"' in cmd.stdout_text

    def test_views_ipa_0043(self, multihost):
        """Adding ipa group and adding group override with gid"""
        groupname = 'ipagroup2'
        viewname = 'gview2'
        gid = '99998'
        multihost.master.kinit_as_admin()
        add_ipa_group(multihost.master, groupname)
        idview_add(multihost.master, viewname)
        cmd = idoverridegroup_add(multihost.master, viewname, groupname, gid)
        print(cmd.stdout_text)
        assert 'GID: 99998' in cmd.stdout_text

    def test_views_ipa_0044(self, multihost):
        """Adding ipa group and adding group override with desc """
        groupname = 'ipagroup3'
        viewname = 'gview3'
        desc = 'testing desc'
        multihost.master.kinit_as_admin()
        add_ipa_group(multihost.master, groupname)
        idview_add(multihost.master, viewname)
        cmd = idoverridegroup_add(multihost.master, viewname,
                                  groupname, desc='testing desc')
        print(cmd.stdout_text)
        assert 'Description: testing desc' in cmd.stdout_text

    def test_views_ipa_0045(self, multihost):
        """Adding ipa group and adding group override with gid and groupname"""
        groupname = 'ipagroup4'
        viewname = 'gview4'
        gid = '123456'
        multihost.master.kinit_as_admin()
        add_ipa_group(multihost.master, groupname)
        idview_add(multihost.master, viewname)
        cmd = idoverridegroup_add(multihost.master, viewname, groupname, gid)
        print(cmd.stdout_text)
        assert 'Anchor to override: ipagroup4' in cmd.stdout_text
        assert 'GID: 123456' in cmd.stdout_text

    def test_views_ipa_0046(self, multihost):
        """Modifying idoverride group with gid"""
        groupname = 'ipagroup5'
        viewname = 'gview5'
        gid = '111111'
        multihost.master.kinit_as_admin()
        cmd = add_ipa_group(multihost.master, groupname)
        print(cmd.stdout_text)
        idview_add(multihost.master, viewname)
        idoverridegroup_add(multihost.master, viewname, groupname)
        cmd1 = idoverridegroup_mod(multihost.master, viewname='gview5',
                                   groupname='ipagroup5', gid='111111')
        print(cmd1.stdout_text)
        print(cmd1.stderr_text)
        assert 'GID: 111111' in cmd1.stdout_text

    def test_views_ipa_0047(self, multihost):
        """Modifying idoverride groupname with groupname option"""
        groupname = 'ipagroup6'
        groupname1 = 'ipagroup66'
        viewname = 'gview6'
        multihost.master.kinit_as_admin()
        cmd = add_ipa_group(multihost.master, groupname)
        print(cmd.stdout_text)
        idview_add(multihost.master, viewname)
        idoverridegroup_add(multihost.master, viewname, groupname)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        add_ipa_group(multihost.master, groupname1)
        cmd1 = idoverridegroup_mod(multihost.master, viewname, groupname,
                                   newgrp='ipagroup66')
        print(cmd1.stdout_text)
        print(cmd1.stderr_text)
        assert 'Modified an Group ID override "ipagroup6"' in cmd1.stdout_text
        assert 'Group name: ipagroup66' in cmd1.stdout_text

    def test_views_ipa_0048(self, multihost):
        """Modifying idoverride groupname with groupname option"""
        groupname = 'ipagroup7'
        groupname1 = 'ipagroup77'
        gid = '111112'
        viewname = 'gview7'
        multihost.master.kinit_as_admin()
        cmd = add_ipa_group(multihost.master, groupname)
        print(cmd.stdout_text)
        idview_add(multihost.master, viewname)
        idoverridegroup_add(multihost.master, viewname, groupname)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        add_ipa_group(multihost.master, groupname1)
        cmd1 = idoverridegroup_mod(multihost.master, viewname, groupname,
                                   gid='111112', newgrp='ipagroup77')
        print(cmd1.stdout_text)
        print(cmd1.stderr_text)
        assert 'Modified an Group ID override "ipagroup7"' in cmd1.stdout_text
        assert 'Group name: ipagroup77' in cmd1.stdout_text
        assert 'GID: 111112' in cmd1.stdout_text

    def test_views_ipa_0049(self, multihost):
        """Modifying idoverride groupname with desc option"""
        groupname = 'ipagroup8'
        desc = 'testing desc'
        viewname = 'gview8'
        multihost.master.kinit_as_admin()
        cmd = add_ipa_group(multihost.master, groupname)
        print(cmd.stdout_text)
        idview_add(multihost.master, viewname)
        cmd1 = idoverridegroup_add(multihost.master, viewname, groupname)
        print(cmd1.stdout_text)
        print(cmd1.stderr_text)
        cmd2 = idoverridegroup_mod(multihost.master, viewname, groupname,
                                   desc='testing desc')
        print(cmd2.stdout_text)
        print(cmd2.stderr_text)
        assert 'Description: testing desc' in cmd2.stdout_text

    def test_views_ipa_0141(self, multihost):
        """idoverridegroup-find with anchor option"""
        cmd1 = add_ipa_group(multihost.master, groupname='idviewgroup1')
        print(cmd1.stdout_text)
        cmd2 = idview_add(multihost.master, viewname='groupview1')
        print(cmd2.stdout_text)
        cmd3 = idoverridegroup_add(multihost.master, viewname='groupview1',
                                   groupname='idviewgroup1')
        print(cmd3.stdout_text)
        cmd4 = idoverridegroup_find(multihost.master, viewname='groupview1',
                                    anchor='idviewgroup1')
        print(cmd4.stdout_text)
        assert '1 Group ID override matched' in cmd4.stdout_text

    def test_views_0049(self, multihost):
        """idoverrideuser find with desc option"""
        multihost.master.kinit_as_admin()
        viewname = 'view9'
        desc = 'testing'
        cmd = idoverrideuser_find(multihost.master, viewname, desc)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        assert 'Description: testing' in cmd.stdout_text

    def test_views_0050(self, multihost):
        """idoverrideuser find with login option"""
        multihost.master.kinit_as_admin()
        viewname = 'view4'
        login = 'user4'
        cmd = idoverrideuser_find(multihost.master, viewname, login)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        assert 'User login: user4' in cmd.stdout_text

    def test_views_ipa_0008(self, multihost):
        """Adding user override with uid and sshpubkey options"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser8')
        idview_add(multihost.master, viewname='ipaview8')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview8',
                                 user='ipauser8', uid='10001',
                                 key='ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0Av'
                                     'eG4i5lVFhcuMasK6VYBKSrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y'
                                     '1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1'
                                     'lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE1qo4+lU+8SIKpFkhJIj'
                                     'l9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== ipauser8@localhost')
        print(cmd.stdout_text)
        assert 'UID: 10001' in cmd.stdout_text
        assert 'SSH public key: ssh-rsa' in cmd.stdout_text

    def test_views_ipa_0010(self, multihost):
        """Adding ipa user override with gidnumber"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser9')
        idview_add(multihost.master, viewname='ipaview9')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview9',
                                 user='ipauser9', gid='10002')
        print(cmd.stdout_text)
        assert 'GID: 10002' in cmd.stdout_text

    def test_views_ipa_0011(self, multihost):
        """Adding ipa user override with gidnumber and login"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser10')
        idview_add(multihost.master, viewname='ipaview10')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview10',
                                 user='ipauser10', gid='10003', login='user10')
        print(cmd.stdout_text)
        assert 'User login: user10' in cmd.stdout_text

    def test_views_ipa_0012(self, multihost):
        """Adding ipa user override with gidnumber and gecos"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser11')
        idview_add(multihost.master, viewname='ipaview11')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview11',
                                 user='ipauser11', gid='10004', gecos='user11')
        print(cmd.stdout_text)
        assert 'GECOS: user11' in cmd.stdout_text

    def test_views_ipa_0013(self, multihost):
        """Adding ipa user override with gidnumber and homedir"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser12')
        idview_add(multihost.master, viewname='ipaview12')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview12',
                                 user='ipauser12', gid='10005',
                                 homedir='/home/ipauser12')
        print(cmd.stdout_text)
        assert 'Home directory: /home/ipauser12' in cmd.stdout_text

    def test_views_ipa_0014(self, multihost):
        """Adding ipa user override with gidnumber and shell"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser13')
        idview_add(multihost.master, viewname='ipaview13')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview13',
                                 user='ipauser13', gid='10006',
                                 shell='/bin/sh')
        print(cmd.stdout_text)
        assert 'Login shell: /bin/sh' in cmd.stdout_text

    def test_views_ipa_0015(self, multihost):
        """Adding ipa user override with gidnumber and sshkey"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser14')
        idview_add(multihost.master, viewname='ipaview14')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview14',
                                 user='ipauser14', gid='10007',
                                 key='ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0Ave'
                                     'G4i5lVFhcuMasK6VYBKSrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1N'
                                     'BrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDH'
                                     'o522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE1qo4+lU+8SIKpFkhJIjl9Jn'
                                     'G/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== ipauser14@localhost')
        print(cmd.stdout_text)
        assert 'GID: 10007' in cmd.stdout_text
        assert 'SSH public key: ssh-rsa' in cmd.stdout_text

    def test_views_ipa_0016(self, multihost):
        """Adding ipa user override with login"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser15')
        idview_add(multihost.master, viewname='ipaview15')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview15',
                                 user='ipauser15', login='user15')
        print(cmd.stdout_text)
        assert 'User login: user15' in cmd.stdout_text

    def test_views_ipa_0017(self, multihost):
        """Adding ipa user override with login and gecos"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser16')
        idview_add(multihost.master, viewname='ipaview16')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview16',
                                 user='ipauser16', login='user16',
                                 gecos='ipauser16')
        print(cmd.stdout_text)
        assert 'User login: user16' in cmd.stdout_text
        assert 'GECOS: ipauser16' in cmd.stdout_text

    def test_views_ipa_0018(self, multihost):
        """Adding ipa user override with login and homedir"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser17')
        idview_add(multihost.master, viewname='ipaview17')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview17',
                                 user='ipauser17', login='user17',
                                 homedir='/home/user17')
        print(cmd.stdout_text)
        assert 'User login: user17' in cmd.stdout_text
        assert 'Home directory: /home/user17' in cmd.stdout_text

    def test_views_ipa_0019(self, multihost):
        """Adding ipa user override with login and shell"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser18')
        idview_add(multihost.master, viewname='ipaview18')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview18',
                                 user='ipauser18', login='user18',
                                 shell='/bin/sh')
        print(cmd.stdout_text)
        assert 'User login: user18' in cmd.stdout_text
        assert 'Login shell: /bin/sh' in cmd.stdout_text

    def test_views_ipa_0020(self, multihost):
        """Adding ipa user override with login and sshpubkey"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser19')
        idview_add(multihost.master, viewname='ipaview19')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview19',
                                 user='ipauser19', login='user19',
                                 key='ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG'
                                     '4i5lVFhcuMasK6VYBKSrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0'
                                     'QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQ'
                                     'CKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq'
                                     '9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== ipauser20@localhost')
        print(cmd.stdout_text)
        assert 'User login: user19' in cmd.stdout_text
        assert 'SSH public key: ssh-rsa' in cmd.stdout_text

    def test_views_ipa_0021(self, multihost):
        """Adding ipa user override with gecos"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser20')
        idview_add(multihost.master, viewname='ipaview20')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview20',
                                 user='ipauser20', gecos='user20')
        print(cmd.stdout_text)
        assert 'GECOS: user20' in cmd.stdout_text

    def test_views_ipa_0022(self, multihost):
        """Adding ipa user override with gecos and homedir"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser21')
        idview_add(multihost.master, viewname='ipaview21')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview21',
                                 user='ipauser21', gecos='user21',
                                 homedir='/home/user21')
        print(cmd.stdout_text)
        assert 'GECOS: user21' in cmd.stdout_text
        assert 'Home directory: /home/user21' in cmd.stdout_text

    def test_views_ipa_0023(self, multihost):
        """Adding ipa user override with gecos and shell"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser22')
        idview_add(multihost.master, viewname='ipaview22')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview22',
                                 user='ipauser22', gecos='user22',
                                 shell='/bin/bash')
        print(cmd.stdout_text)
        assert 'GECOS: user22' in cmd.stdout_text
        assert 'Login shell: /bin/bash' in cmd.stdout_text

    def test_views_ipa_0024(self, multihost):
        """Adding ipa user override with gecos and sshpubkey"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipausr19')
        idview_add(multihost.master, viewname='ipaview19')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview19',
                                 user='ipausr19', gecos='ipausr19',
                                 key='ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG'
                                     '4i5lVFhcuMasK6VYBKSrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0'
                                     'QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQ'
                                     'CKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq'
                                     '9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== ipauser19@localhost')
        print(cmd.stdout_text)
        assert 'GECOS: ipausr19' in cmd.stdout_text
        assert 'SSH public key: ssh-rsa' in cmd.stdout_text

    def test_views_ipa_0025(self, multihost):
        """Adding ipa user override with homedir option"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser23')
        idview_add(multihost.master, viewname='ipaview23')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview23',
                                 user='ipauser23', homedir='/home/ipauser23')
        print(cmd.stdout_text)
        assert 'Home directory: /home/ipauser23' in cmd.stdout_text

    def test_views_ipa_0026(self, multihost):
        """Adding ipa user override with homedir and shell option"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser24')
        idview_add(multihost.master, viewname='ipaview24')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview24',
                                 user='ipauser24', shell='/bin/bash')
        print(cmd.stdout_text)
        assert 'Login shell: /bin/bash' in cmd.stdout_text

    def test_views_ipa_0027(self, multihost):
        """Adding ipa user override with homedir and sshpubkey"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser25')
        idview_add(multihost.master, viewname='ipaview25')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview25',
                                 user='ipauser25', homedir='/home/ipauser25',
                                 key='ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG'
                                     '4i5lVFhcuMasK6VYBKSrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0'
                                     'QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQ'
                                     'CKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq'
                                     '9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== ipauser25@localhost')
        print(cmd.stdout_text)
        assert 'Home directory: /home/ipauser25' in cmd.stdout_text
        assert 'SSH public key: ssh-rsa' in cmd.stdout_text

    def test_views_ipa_0028(self, multihost):
        """Adding ipa user override with shell option"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser26')
        idview_add(multihost.master, viewname='ipaview26')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview26',
                                 user='ipauser26', shell='/bin/sh')
        print(cmd.stdout_text)
        assert 'Login shell: /bin/sh' in cmd.stdout_text

    def test_views_ipa_0029(self, multihost):
        """Adding ipa user override with shell and sshpubkey"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser27')
        idview_add(multihost.master, viewname='ipaview27')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview27',
                                 user='ipauser27', shell='/bin/bash',
                                 key='ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG'
                                     '4i5lVFhcuMasK6VYBKSrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0'
                                     'QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQ'
                                     'CKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq'
                                     '9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== ipauser27@localhost')
        print(cmd.stdout_text)
        assert 'Login shell: /bin/bash' in cmd.stdout_text
        assert 'SSH public key: ssh-rsa' in cmd.stdout_text

    def test_views_ipa_0030(self, multihost):
        """Adding ipa user override with sshpubkey only"""
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser28')
        idview_add(multihost.master, viewname='ipaview28')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview28',
                                 user='ipauser28',
                                 key='ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG'
                                     '4i5lVFhcuMasK6VYBKSrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0'
                                     'QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQ'
                                     'CKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq'
                                     '9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== ipauser28@localhost')
        print(cmd.stdout_text)
        assert 'SSH public key: ssh-rsa' in cmd.stdout_text

    def test_views_ipa_0031(self, multihost):
        """Adding ipa user override with all options """
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user='ipauser29')
        idview_add(multihost.master, viewname='ipaview29')
        cmd = idoverrideuser_add(multihost.master, viewname='ipaview29',
                                 user='ipauser29', uid='213313',
                                 login='user29',
                                 homedir='/home/ipauser29', desc='testuser',
                                 gid='213313', shell='/bin/sh',
                                 key='ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG'
                                     '4i5lVFhcuMasK6VYBKSrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0'
                                     'QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQ'
                                     'CKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE23o4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq'
                                     '9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== ipauser29@localhost')
        print(cmd.stdout_text)
        assert 'Description: testuser' in cmd.stdout_text
        assert 'User login: user29' in cmd.stdout_text
        assert 'UID: 213313' in cmd.stdout_text
        assert 'GID: 213313' in cmd.stdout_text
        assert 'Home directory: /home/ipauser29' in cmd.stdout_text
        assert 'Login shell: /bin/sh' in cmd.stdout_text
        assert 'SSH public key: ssh-rsa' in cmd.stdout_text

    def test_userdel_domain(self, multihost):
        multihost.master.kinit_as_admin()
        check_rpm(multihost.master, ['adcli'])
        for i in range(30):
            multihost.master.run_command(['adcli', 'delete-user',
                                                '--domain=' + multihost.master.config.ad_top_domain,
                                                'idviewuser%s' % str(i)],
                                               stdin_text=multihost.master.config.ad_pwd,
                                               raiseonerr=False)

    def test_groupdel_domain(self, multihost):
        multihost.master.kinit_as_admin()
        check_rpm(multihost.master, ['adcli'])
        for i in range(20):
            multihost.master.run_command(['adcli', 'delete-group',
                                                '--domain=' + multihost.master.config.ad_top_domain,
                                                'idviewgroup%s' % str(i)],
                                               stdin_text=multihost.master.config.ad_pwd,
                                               raiseonerr=False)

    def class_teardown(self, multihost):
        multihost.master.qerun(
            'ipa trust-del ' + multihost.master.config.ad_top_domain)
        uninstall_server(multihost.master)
