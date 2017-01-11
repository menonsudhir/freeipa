"""
Overview: IDView Testcase automation
"""

import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.utils import service_control, disable_dnssec, dnsforwardzone_add
from ipa_pytests.shared.rpm_utils import check_rpm


class Testidview(object):
    """ Test Class """

    def class_setup(self, multihost):
        """ Setup for class """
        print "\nClass Setup"
        print "MASTER: ", multihost.master.hostname
        print "CLIENT: ", multihost.client.hostname

    def test_disable_dnssec(self, multihost):
        """Disable's DNSSEC and restart named-pkcs11 service"""
        multihost.master.kinit_as_admin()
        disable_dnssec(multihost.master)
        service_control(multihost.master, 'named-pkcs11', 'restart')

    def test_add_dnsforwardzoneipa(self, multihost):
        """Adding forwardzone polcy for Windows AD domain"""
        multihost.master.kinit_as_admin()
	dnsforwardzone_add(multihost.master, multihost.master.config.ad_top_domain, multihost.master.config.dns_forwarder)

    def test_adtrust_install(self, multihost):
        """Setting up smb.conf for AD trust using ipa-adtrust-install command """
        multihost.master.kinit_as_admin()
        check_rpm(multihost.master, 'ipa-server-trust-ad')
        multihost.master.qerun(['ipa-adtrust-install',
                                '--netbios-name=' + multihost.master.config.net_name,
                                '-a',
                                'admin_pwd',
                                '-U'])

    def test_activedir_password(self, multihost):
        """Adding trust with Windows AD """
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
            print output.stderr_text
        else:
            print output.stdout_text

    def test_add_aduser(self, multihost):
        """adduser.sh adds active directory user in AD"""
        multihost.master.kinit_as_admin()
        cmd = "sh -x /root/code/ipa-pytests/ipa-idoverride/adduser.sh " + multihost.master.config.ad_hostname
        with open('test4.exp', 'w') as f:
            f.write('set timeout 5\n')
            f.write('set force_conservative 0\n')
            f.write('set send_slow {1.1}\n')
            f.write('spawn %s\n' % (cmd))
            f.write("expect \"Password for Administrator@" + multihost.master.config.ad_top_domain + "\"\n")
            f.write('send -s -- \"Secret123\\r"\n')
            f.write('expect eof')
        multihost.master.transport.put_file('test4.exp', '/tmp/test4.exp')
        output = multihost.master.run_command(['expect', '/tmp/test4.exp'], raiseonerr=False)
        if output.returncode != 0:
            print output.stderr_text
        else:
            print output.stdout_text

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
        output = multihost.master.run_command(['expect', '/tmp/test2.exp'], raiseonerr=False)
        if output.returncode != 0:
            print output.stderr_text
        else:
            print output.stdout_text

    def test_0071_addwithoutoptions(self, multihost):
        """Adding view using idview-add command"""
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'idview-add', 'TestView2'],
                               exp_returncode=0,
                               exp_output='Added ID View "TestView2"')

    def test_0072_adddescription(self, multihost):
        """Adding view using idview-add command and desc option"""
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'idview-add', 'TestView6', '--desc=view6'],
                               exp_returncode=0,
                               exp_output='Description: view6')

    def test_0073_addsameviewagain(self, multihost):
        """Adding view which already exists"""
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'idview-add', 'TestView6'],
                               exp_returncode=1,
                               exp_output='ipa: ERROR: ID View with name "TestView6" already exists')

    def test_0074_differentcase(self, multihost):
        """Adding view which already exists but with differentcase"""
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'idview-add', 'TESTVIEW6'],
                               exp_returncode=1,
                               exp_output='ipa: ERROR: ID View with name "TESTVIEW6" already exists')

    def test_0090_findname(self, multihost):
        """Find a specific view using idview-find command"""
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'idview-find', 'TestView6'],
                               exp_returncode=0,
                               exp_output='Number of entries returned 1')

    def test_0091_finddesc(self, multihost):
        """Find a specific view using  desc option"""
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'idview-find', '--desc=view6'],
                               exp_returncode=0,
                               exp_output='Number of entries returned 1')

    def test_0092_findall(self, multihost):
        """Find all views on the IPA  box"""
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'idview-find', '--all'],
                               exp_returncode=0,
                               exp_output='4 ID Views matched')

    def test_0093_findraw(self, multihost):
        """Need to check this one"""
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'idview-find', '--all'],
                               exp_returncode=0,
                               exp_output='4 ID Views matched')

    def test_0094_findallraw(self, multihost):
        """Find views using all and raw option"""
        multihost.master.qerun(['ipa', 'idview-find', '--all', '--raw'],
                               exp_returncode=0,
                               exp_output='4 ID Views matched')

    def test_0095_findsizelimit(self, multihost):
        """Find idview with specified sizelimit """
        multihost.master.qerun(['ipa', 'idview-find', '--sizelimit=2'],
                               exp_returncode=0, exp_output='2 ID Views matched')

    def test_0096_findcaseinsensitive(self, multihost):
        """Find idview  as case insensitive option"""
        multihost.master.qerun(['ipa', 'idview-find', 'TESTVIEW2'],
                               exp_returncode=0, exp_output='1 ID View matched')

    def test_0098_modrename(self, multihost):
        """Renaming idviews using rename option"""
        multihost.master.qerun(['ipa', 'idview-mod', 'testview', '--rename=view'],
                               exp_returncode=0, exp_output='ID View Name: view')

    def test_0099_moddescription(self, multihost):
        """Modify idview using desc  option"""
        multihost.master.qerun(['ipa', 'idview-mod', 'testview2', '--desc=view2'],
                               exp_returncode=0, exp_output='Description: view2')

    def test_0100_moddefaulttrust(self, multihost):
        """Modify default trust view """
        multihost.master.qerun(['ipa', 'idview-mod', 'default trust view'],
                               exp_returncode=1,
                               exp_output='ipa: ERROR: ID View Default Trust View cannot be deleted/modified: system ID View')

    def test_0002_useradd(self, multihost):
        """Adding user to specific view"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser1@'
                                + multihost.master.config.ad_top_domain],
                               exp_returncode=0,
                               exp_output='Added User ID override "idviewuser1@' + multihost.master.config.ad_top_domain)

    def test_0003_useradduid(self, multihost):
        """Trusted AD user is added to view  using uid option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser2@'
                                + multihost.master.config.ad_top_domain, '--uid=200000'],
                               exp_returncode=0,
                               exp_output='Added User ID override "idviewuser2@' + multihost.master.config.ad_top_domain)

    def test_0004_sameuidgid(self, multihost):
        """Trusted AD user is added to view  using uid, gidnumber option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser3@'
                                + multihost.master.config.ad_top_domain,
                                '--uid=200000', '--gidnumber=200000'], exp_returncode=0,
                               exp_output='Added User ID override "idviewuser3@' + multihost.master.config.ad_top_domain)

    def test_0005_diffuidgid(self, multihost):
        """Trusted AD user is added to view  using uid, gidnumber option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser4@'
                                + multihost.master.config.ad_top_domain,
                                '--uid=200000', '--gidnumber=200001'], exp_returncode=0,
                               exp_output='Added User ID override "idviewuser4@' + multihost.master.config.ad_top_domain)

    def test_0006_adduidlogin(self, multihost):
        """Trusted AD user is added to view  using uid, login option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser5@'
                                + multihost.master.config.ad_top_domain,
                                '--uid=30000', '--login=user5'],
                               exp_returncode=0, exp_output='User login: user5')

    def test_0007_adduidgecos(self, multihost):
        """Trusted AD user is added to view  using uid, gecos option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser6@'
                                + multihost.master.config.ad_top_domain,
                                '--uid=30001', '--gecos=user6'],
                               exp_returncode=0, exp_output='GECOS: user6')

    def test_0008_adduidhomedir(self, multihost):
        """Trusted AD user is added to view  using uid, homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser7@'
                                + multihost.master.config.ad_top_domain,
                                '--uid=30002', '--homedir=/home/user7'], exp_returncode=0,
                               exp_output='Home directory: /home/user7')

    def test_0009_adduidshell(self, multihost):
        """Trusted AD user is added to view using uid shell option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser8@'
                                + multihost.master.config.ad_top_domain,
                                '--uid=30003', '--shell=/bin/sh'], exp_returncode=0,
                               exp_output='Login shell: /bin/sh')

    def test_0011_adduiddesc(self, multihost):
        """Trusted AD user is added to view using uid and desc option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser10@'
                                + multihost.master.config.ad_top_domain,
                                '--uid=30005', '--desc=USER10'],
                               exp_returncode=0, exp_output='Description: USER10')

    def test_0012_addgidnumber(self, multihost):
        """Trusted AD user is added to view using gid option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser11@'
                                + multihost.master.config.ad_top_domain,
                                '--gid=40001'], exp_returncode=0, exp_output='GID: 40001')

    def test_0013_addgidnumberlogin(self, multihost):
        """Trusted AD user is added to view using gid and login option """
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser12@'
                                + multihost.master.config.ad_top_domain,
                                '--gid=40002', '--login=user12'], exp_returncode=0,
                               exp_output='User login: user12')

    def test_0014_addgidgecos(self, multihost):
        """Trusted AD user is added to view using gid and gecos option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser13@'
                                + multihost.master.config.ad_top_domain,
                                '--gid=40003', '--gecos=gecostest'],
                               exp_returncode=0, exp_output='GECOS: gecostest')

    def test_0015_addgidgecoshomedir(self, multihost):
        """Trusted AD user is added to view using gid and homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser14@'
                                + multihost.master.config.ad_top_domain,
                                '--gid=40004', '--homedir=/home/user14'],
                               exp_returncode=0, exp_output='Home directory: /home/user14')

    def test_0016_addgidshell(self, multihost):
        """Trusted AD user is added to view using shell and gid option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser15@'
                                + multihost.master.config.ad_top_domain,
                                '--gid=40005', '--shell=/bin/sh'],
                               exp_returncode=0, exp_output='Login shell: /bin/sh')

    def test_0018_addlogin(self, multihost):
        """Trusted AD user  is added to view along with --login option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser17@'
                                + multihost.master.config.ad_top_domain,
                                '--login=user17'], exp_returncode=0,
                               exp_output='User login: user17')

    def test_0019_logingecos(self, multihost):
        """Trusted AD user  is added to view along with  login and gecos option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain,
                                '--login=user18', '--gecos=valid user'], exp_returncode=0,
                               exp_output='GECOS: valid user')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain], exp_returncode=0)

    def test_0020_loginhomedir(self, multihost):
        """Trusted AD user is added to view along with login and homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain,
                                '--login=user18', '--homedir=/home/test'], exp_returncode=0,
                               exp_output='Home directory: /home/test')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain], exp_returncode=0)

    def test_0021_loginshell(self, multihost):
        """
        Trusted AD user is added to view along with login and shell option
        """
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain,
                                '--login=user18', '--shell=/bin/sh'], exp_returncode=0,
                               exp_output='Login shell: /bin/sh')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain], exp_returncode=0)

    def test_0023_addgecos(self, multihost):
        """Trusted AD user is added to view along with gecos option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain,
                                '--gecos=user18'], exp_returncode=0,
                               exp_output='GECOS: user18')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain], exp_returncode=0)

    def test_0024_addgecoshomedir(self, multihost):
        """Trusted AD user is added to view along with gecos and homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain,
                                '--gecos="user18"', '--homedir=/home/test'], exp_returncode=0,
                               exp_output='Home directory: /home/test')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain], exp_returncode=0)

    def test_0025_addgecosshell(self, multihost):
        """Trusted AD user is added to view along with gecos and shell option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain,
                                '--gecos="user18"', '--shell=/bin/bash'], exp_returncode=0,
                               exp_output='Login shell: /bin/bash')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain], exp_returncode=0)

    def test_0027_addhomedir(self, multihost):
        """Trusted AD user is added to view with homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain,
                                '--homedir=/home/test'], exp_returncode=0,
                               exp_output='Home directory: /home/test')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain], exp_returncode=0)

    def test_0028_homedirshell(self, multihost):
        """Trusted AD user is added to view with homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain,
                                '--homedir=/home/test'], exp_returncode=0,
                               exp_output='Home directory: /home/test')
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain], exp_returncode=0)

    def test_0030_addshell(self, multihost):
        """Trusted AD user is added to view with shell option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain,
                                '--shell=/bin/sh'], exp_returncode=0,
                               exp_output='Login shell: /bin/sh')

    def test_0036_moddesc(self, multihost):
        """Trusted AD user in view is modified with desc option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain,
                                '--desc=desc1'], exp_returncode=0,
                               exp_output='Description: desc1')

    def test_0037_modlogin(self, multihost):
        """Trusted AD user in view is modified with login option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain,
                                '--login=moduser1'], exp_returncode=0,
                               exp_output='User login: moduser1')

    def test_0038_moduid(self, multihost):
        """Trusted AD user in view is modified with uid option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain,
                                '--uid=55555'], exp_returncode=0,
                               exp_output='UID: 55555')

    def test_0039_modgecos(self, multihost):
        """Trusted AD user in view is modified with gecos option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain,
                                '--gecos=User18'], exp_returncode=0,
                               exp_output='GECOS: User18')

    def test_0040_modgidnumber(self, multihost):
        """Trusted AD user in view is modified with gidnumber option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain,
                                '--gidnumber=777777'], exp_returncode=0,
                               exp_output='GID: 777777')

    def test_0041_modhomedir(self, multihost):
        """Trusted AD user in view is modified with homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain,
                                '--homedir=/home/user18'], exp_returncode=0,
                               exp_output='Home directory: /home/user18')

    def test_0042_modshell(self, multihost):
        """Trusted AD user in view is modified with shell option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view', 'idviewuser1@'
                                + multihost.master.config.ad_top_domain,
                                '--shell=/bin/sh'], exp_returncode=0,
                               exp_output='Login shell: /bin/sh')

    def test_0049_finddesc(self, multihost):
        """Finding trusted AD user in view using desc option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-find', 'view', '--desc=USER10'],
                               exp_returncode=0,
                               exp_output='Number of entries returned 1')

    def test_0050_findlogin(self, multihost):
        """Finding trusted AD user in view using login option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-find', 'view', '--login=user17'],
                               exp_returncode=0,
                               exp_output='Number of entries returned 1')

    def test_0051_finduid(self, multihost):
        """Finding trusted AD user in view using uid option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-find', 'view', '--uid=30005'],
                               exp_returncode=0,
                               exp_output='Number of entries returned 1')

    def test_0052_findgecos(self, multihost):
        """Finding trusted AD user in view using gecos option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-find', 'view', '--gecos=gecostest'],
                               exp_returncode=0,
                               exp_output='Number of entries returned 1')

    def test_0053_findgidnumber(self, multihost):
        """Finding trusted AD user in view using gidnumber option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-find', 'view', '--gidnumber=40001'],
                               exp_returncode=0,
                               exp_output='Number of entries returned 1')

    def test_0054_findhomedir(self, multihost):
        """Finding trusted AD user in view using homedir option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-find', 'view', '--homedir=/home/user7'],
                               exp_returncode=0,
                               exp_output='Number of entries returned 1')

    def test_0055_findshell(self, multihost):
        """Finding trusted AD user in view using shell option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-find', 'view', '--shell=/bin/sh'],
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
        multihost.master.qerun(['ipa', 'idoverrideuser-find', 'view', '--raw', '--all'],
                               exp_returncode=0,
                               exp_output='objectClass: *')

    def test_0059_findpkeyonly(self, multihost):
        """Find overridden user with --pkeyonly option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-find', 'view', '--pkey-only'],
                               exp_returncode=0,
                               exp_output='Number of entries returned *')

    def test_0064_showall(self, multihost):
        """Finding trusted AD user in view using show all option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-show', 'view', 'idviewuser1@'
                                + multihost.master.config.ad_top_domain, '--all'],
                               exp_returncode=0,
                               exp_output='objectclass: ')

    def test_0065_showraw(self, multihost):
        """Finding trusted AD user in view using show raw option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-show', 'view', 'idviewuser1@'
                                + multihost.master.config.ad_top_domain, '--raw'],
                               exp_returncode=0,
                               exp_output='ipaanchoruuid: :SID:')

    def test_0066_showall(self, multihost):
        """Finding trusted AD user in view using show all raw option"""
        multihost.master.qerun(['ipa', 'idoverrideuser-show', 'view', 'idviewuser1@'
                                + multihost.master.config.ad_top_domain, '--all'],
                               exp_returncode=0,
                               exp_output='dn: ipaanchoruuid=')

    def test_0069_idoverridedel(self, multihost):
        """Deleting a idoverride user from the view"""
        multihost.master.qerun(['ipa', 'idoverrideuser-del', 'view', 'idviewuser18@'
                                + multihost.master.config.ad_top_domain],
                               exp_returncode=0)

    def test_0010_idoverride_uid_sshpubkey(self, multihost):
        """Adding a user with uid and pubkey"""
        multihost.master.kinit_as_admin()
        uid = '899989'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKSrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser21@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser21@'
                                + multihost.master.config.ad_top_domain,
                                '--sshpubkey''=' + key,
                                '--uid''=' + uid],
                               exp_returncode=0)

    def test_0017_idoverride_gid_sshpubkey(self, multihost):
        """Adding a user with gidnumber and pubkey"""
        multihost.master.kinit_as_admin()
        gid = '899989'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKSrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser22@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser22@'
                                + multihost.master.config.ad_top_domain,
                                '--sshpubkey''=' + key,
                                '--gidnumber''=' + gid],
                               exp_returncode=0)

    def test_0022_idoverride_login_sshpubkey(self, multihost):
        """Adding a user with login and pubkey"""
        multihost.master.kinit_as_admin()
        login = 'user23'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKSrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser23@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser23@'
                                + multihost.master.config.ad_top_domain,
                                '--sshpubkey''=' + key,
                                '--login''=' + login],
                               exp_returncode=0)

    def test_0026_idoverride_gecos_sshpubkey(self, multihost):
        """Adding a user with gecos and pubkey"""
        multihost.master.kinit_as_admin()
        gecos = 'testuser'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKSrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser24@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser24@'
                                + multihost.master.config.ad_top_domain,
                                '--sshpubkey''=' + key,
                                '--gecos''=' + gecos],
                               exp_returncode=0)

    def test_0031_idoverride_shell_sshpubkey(self, multihost):
        """Adding a user with gecos and pubkey"""
        multihost.master.kinit_as_admin()
        shell = '/bin/bash'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKSrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser25@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser25@'
                                + multihost.master.config.ad_top_domain,
                                '--sshpubkey''=' + key,
                                '--homedir''=' + shell],
                               exp_returncode=0)

    def test_0029_idoverride_homedir_sshpubkey(self, multihost):
        """Adding a user with gecos and pubkey"""
        multihost.master.kinit_as_admin()
        homedir = '/home/ipaaduser'
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKSrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser26@localhost'
        multihost.master.qerun(['ipa', 'idoverrideuser-add', 'view', 'idviewuser26@'
                                + multihost.master.config.ad_top_domain,
                                '--sshpubkey''=' + key,
                                '--homedir''=' + homedir],
                               exp_returncode=0)

    def test_0043_idoverrideuser_mod_sshpubkey(self, multihost):
        """modifying a user pubkey"""
        multihost.master.kinit_as_admin()
        key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAx0Hg3CZIzizMIohZydE5+cSgIyByWmD0r/J5+k2P0AveG4i5lVFhcuMasK6VYBKSrFxSgpgkw5M82Ven2lyDpFoPbPJFE8KW6eLoRPCYPO+BBaI2j9t90HueoT2y1NBrKo0QTk5fCSSGN3kKuMUCgcqQw/9ea39dFAI96szAVfk+Y1eg1E84iOg1a/usFft0r+UuOd6bxzu/1lDHo522tIhiQCKAAyxOGij3w6Zw4mfFu/99l3LKm+ACAFpeAWkJqCjfku2WIkE1qo4+lU+8SIKpFkhJIjl9JnG/9ecuMWAhiZq9Ny4lypXogbVOPZThd2nAP3x+//t7+Vrq+VXjCQ== idviewuser26@modified'
        multihost.master.qerun(['ipa', 'idoverrideuser-mod', 'view', 'idviewuser26@'
                                + multihost.master.config.ad_top_domain,
                                '--sshpubkey''=' + key],
                               exp_returncode=0)

    def test_0076_applydefaulttrustview(self, multihost):
        """Applying default trust view to a host"""
        hostname = 'hosts.testdomain.com'
        multihost.master.qerun(['ipa', 'idview-apply', 'default trust view', '--hosts=' + hostname],
                               exp_returncode=1,
                               exp_output="ipa: ERROR: invalid 'ID View': Default Trust View cannot be applied on hosts")

    def test_0077_emptydeftrustview(self, multihost):
        """Applying default trust view with no value to host"""
        multihost.master.qerun(['ipa', 'idview-apply', 'view', '--hosts=\" \"'],
                               exp_returncode=0,
                               exp_output='Number of hosts the ID View was applied to: 0')

    def test_0078_nonexistinghost(self, multihost):
        """Applying view to non existing host"""
        hostname = 'host.test123.com'
        multihost.master.qerun(['ipa', 'idview-apply', 'view', '--hosts=' + hostname],
                               exp_returncode=1,
                               exp_output='hosts: host.test123.com: not found')

    def test_0079_nonexistingview(self, multihost):
        """Applying a non existing view"""
        hostname = 'host.test123.com'
        multihost.master.qerun(['ipa', 'idview-apply', 'abc ', '--hosts=' + hostname],
                               exp_returncode=2,
                               exp_output='ipa: ERROR: no such entry')

    def test_0048_overridefind_anchor(self, multihost):
        """idoverride find using anchor """
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'idoverrideuser-find', 'view', '--anchor=idviewuser18@'
                                +multihost.master.config.ad_top_domain], exp_returncode=0,
                               exp_output='1 User ID overrides matched')
