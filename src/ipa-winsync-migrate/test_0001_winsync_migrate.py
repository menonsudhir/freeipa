"""
ipa-winsync-migration tool automation
BZ#1204205 - [RFE] ID Views: Automated migration tool from Winsync to Trusts
"""
import re
import time
import pytest
from ipa_pytests.shared import paths
from datetime import datetime, timedelta
from ipa_pytests.shared.utils import (service_control,
                                      dnsforwardzone_add, add_dnsforwarder,
                                      disable_dnssec)
from  ipa_pytests.shared.user_utils import (add_ipa_user)
from ipa_pytests.shared.trust_utils import check_for_skew


class TestWinSyncMigrate(object):
    """ Test Class """

    def class_setup(self, multihost):
        """ Setup for class """
        master1 = multihost.master
        master1.kinit_as_admin()
        ad1 = multihost.ads[0]
        adserver = ad1.external_hostname
        multihost.passwd = 'Secret123'
        netbios_name = ad1.domain.name.split(".")[0].upper()
        ad_domain_name = adserver.split(".")[1]
        ad_sname = adserver.split(".")[0].upper()
        slapdname = master1.domain.realm.upper().replace('.', '-')
        slapdname = '/etc/dirsrv/slapd-' + slapdname
        named_conf = '/etc/named.conf'
        sleep_time = 20

        # Info
        print("Using following hosts for IPA WinSync Migration testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("Windows AD Server: %s" % adserver)
        print("*" * 80)

        # Checking for required RPMs installed on Master
        cmd = 'dnf module install idm:DL1/adtrust'
        multihost.master.qerun(cmd, exp_returncode=0)

        # Check time between two server
        synced = check_for_skew(master1, ad1)
        if synced:
            print("IPA server time and AD server time in sync, "
                  "Proceeding...")
        else:
            print("Time skew between IPA Server and AD Server greater "
                  "than 1 minute. Please sync time and try again.")
            pytest.fail("Clock skew greater than 1 minute")

        # Step 1: Export Certificate from CRT to CER format
        print("1. Export AD Certificate from CRT TO CER Format")
        path = "C:\\\\Windows\\\\System32\\\\CertSrv\\\\CertEnroll\\\\"
        # Certificate created by AD Certificate services are in this format
        # hydra.testipa.in_testipa-HYDRA-CA.crt
        crtfile = "{}{}_{}-{}-CA.crt".format(path,
                                             adserver,
                                             ad_domain_name,
                                             ad_sname)
        adcerfile = "C:\\\\ADCert.cer"
        ipacertfile = "/cygdrive/c/IPAcert.cer"

        # Delete any existing AD certificate files on AD server
        if ad1.transport.file_exists(adcerfile):
            ad1.transport.remove_file(adcerfile)

        # Exporting certificate to base64 format on AD server
        cmdstr = ['certutil', '-encode', crtfile, adcerfile]
        cmd = ad1.run_command(cmdstr, raiseonerr=False)
        if "command completed successfully" not in cmd.stdout_text:
            print(cmd.returncode, cmd.stdout_text, cmd.stderr_text)
            pytest.fail("Failed to export AD certificate from "
                        "CRT [%s] to CER [%s]" % (crtfile, adcerfile))
        else:
            print("Successfully exported AD certificate from CRT [%s]"
                  " to CER [%s]" % (crtfile, adcerfile))

        # Disable DNSSec validation
        print("Disabling DNSSec validation in named server")
        disable_dnssec(master1)

        print("Adding DNS forwardzone for AD server")
        dnsforwardzone_add(master1, ad1.domain.name, ad1.ip)

        # Add DNS forwarder from AD side
        print("Adding DNS forwarder of IPA server [%s] "
              "on AD Server [%s]" % (master1.hostname, adserver))
        add_dnsforwarder(master1, master1.hostname, master1.ip)

        # Adding two-way trust with Windows'''
        print("Sleeping for [%d] seconds" % (sleep_time))
        time.sleep(sleep_time)

        # Verify DNS Zone add
        print("Verifying DNS Zone on IPA server [%s]" % (master1.hostname))
        for i in [master1.domain.name, ad1.domain.name]:
            cmdstr = ['dig', 'SRV', '_ldap._tcp.{}'.format(i)]
            print("Running command : [%s]" % " ".join(cmdstr))
            master1.qerun(cmdstr, exp_output="ANSWER: 1")

        print("2. Copy IPA Certificate to AD server")
        # Step 2: Copy IPA certificate to AD server
        cfg = master1.get_file_contents('/etc/ipa/ca.crt')
        cmd = ad1.put_file_contents(ipacertfile, cfg)
        # Copy AD certificate to IPA Server
        cfg = ad1.get_file_contents(adcerfile)
        adcertfile_ipa = slapdname + '/ADCert.cer'
        cmd = master1.put_file_contents(adcertfile_ipa, cfg)

        print("3. Import AD certificate to IPA Server")
        # Step 3: Import AD certificate to IPA server
        if master1.transport.file_exists(slapdname):
            cmd = master1.run_command('certutil -d ' + slapdname +
                                      ' -A -i ' + adcertfile_ipa +
                                      ' -n "AD Server Cert"' +
                                      ' -t "CT,C,C" -a',
                                      raiseonerr=False)
            if cmd.returncode != 0:
                print(cmd.stderr_text, cmd.stdout_text)
                pytest.fail("Unable to add AD certificate in IPA server")
            cmd = master1.run_command('certutil -d ' + slapdname + ' -L',
                                      raiseonerr=False)
            print("Output of certutil :\n" + cmd.stdout_text)
        else:
            print(cmd.stderr_text, cmd.stdout_text)
            pytest.fail("Unable to find slapd instance directory at [%s]"
                        % (slapdname))

        # Deleting the winsync agreement before doing winsync migration
        excpectoutput = '\'{}\''.format(master1.hostname) + " has no winsync replication agreement for "'\'{}\''.format(
            adserver)
        multihost.master.qerun(['ipa-replica-manage', 'disconnect', adserver], exp_returncode=1,
                               exp_output=excpectoutput)

        dc1 = adserver.split(".")[1]
        dc2 = adserver.split(".")[2]
        dc = 'cn=Administrator,cn=Users,' + 'dc=%s,' % dc1 + 'dc=%s' % dc2

        cmdstr = 'ipa-replica-manage connect --winsync --passsync=' + \
                 multihost.passwd + ' --cacert=' + adcertfile_ipa + ' ' + \
                 adserver + ' --binddn=' + dc + \
                 ' --bindpw ' + '\'Secret123\'' + ' -v -p ' + 'Secret123'

        print("Running command : %s" % (cmdstr))
        cmd = master1.run_command(cmdstr, raiseonerr=False)
        if cmd.returncode != 0:
            print(cmd.stdout_text, cmd.stderr_text)
            pytest.fail("Unable to run ipa-replica-manage")

        cmd = master1.run_command('ipa-replica-manage list', raiseonerr=False)
        if cmd.returncode == 0 and adserver in cmd.stdout_text:
            print("Successfully configured replica between AD server "
                  "and IPA server")
        else:
            pytest.fail("Failed to verify replica connection between "
                        "AD server and IPA server")


        print("Running ipa-adtrust-install on %s" % (master1.hostname))
        # Add ad trust in IPA server
        print("Adding Cross Realm AD-trust between IPA server [%s] "
              "and AD server [%s]" % (master1.hostname, adserver))

        cmd = master1.run_command('ipa-adtrust-install -a ' +
                                  multihost.passwd + '-A admin ' +
                                  '--netbios-name=' + master1.netbios +
                                  ' -U', raiseonerr=False)
        if cmd.returncode != 0:
            pytest.fail("Unable to install ipa-adtrust-install on [%s] "
                        % (master1.hostname))

        cmdstr = ['ipa', 'trust-add', '--range-type="ipa-ad-trust"',
                  '--two-way="true"', ad1.domain.name,
                  '--admin={}'.format(ad1.username)]

        print("Running command : %s" % (cmdstr))
        cmd = master1.run_command(cmdstr,
                                  stdin_text=ad1.password,
                                  raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if cmd.returncode != 0:
            pytest.fail("Failed to add AD trust between AD Server [%s] "
                        " and IPA server [%s]"
                        % (master1.hostname, adserver))

    def test_0001_bz1204205(self, multihost):
        """
        test_0001_winsync_migrate
        Verify BZ1204205
        """
        print("Automation for BZ#1204205")
        master1 = multihost.master
        ad1 = multihost.ads[0]
        master1.kinit_as_admin()

        cmd = master1.run_command('ipa-replica-manage list', raiseonerr=False)
        if cmd.returncode == 0 and ad1.hostname in cmd.stdout_text:
            print("Replica agreement available between AD server "
                  "and IPA server")
        else:
            pytest.fail("Failed to verify replica connection between "
                        "AD server and IPA server")

        adserver = ad1.external_hostname
        adrelm = ad1.domain.name.upper()
        cmdstr = ["ipa-winsync-migrate", "--server={}".format(adserver), "--realm={}".format(adrelm)]
        cmd = master1.run_command(cmdstr, raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if cmd.returncode != 0:
            pytest.fail("Failed to run [%s] " % " ".join(cmdstr))

        # Add users and groups
        ext = "0001"
        iview = 'hostview1_' + ext
        user1 = 'testuser1_' + ext
        user2 = 'testuser2_' + ext
        group1 = 'ipagrp1_' + ext
        group2 = 'grp1_' + ext

        for i in [user1, user2]:
            cmdstr = ['adcli', 'create-user', i, '-D', ad1.domain.name]
            print("Running command : %s" % " ".join(cmdstr))
            cmd = master1.run_command(cmdstr,
                                      stdin_text=ad1.password,
                                      raiseonerr=False)
            if cmd.returncode != 0:
                print(cmd.stdout_text, cmd.stderr_text)
                pytest.fail("Failed to add user [%s]" % (i))

        for j in [group1, group2]:
            cmdstr = ['adcli', 'create-group', j, '-D', ad1.domain.name]
            cmd = master1.run_command(cmdstr,
                                      stdin_text=ad1.password,
                                      raiseonerr=False)
            if cmd.returncode != 0:
                pytest.fail("Failed to add group [%s] " % (j))

        cmdstr = ['adcli', 'add-member', group2, user1, user2,
                  '-D' + ad1.domain.name]
        cmd = master1.run_command(cmdstr,
                                  stdin_text=ad1.password,
                                  raiseonerr=False)
        if cmd.returncode != 0:
            pytest.fail("Failed to add user in group using adcli command")

        cmdstr = ['ipa', 'idview-add', iview]
        print("Running command : %s" % " ".join(cmdstr))
        cmd = master1.run_command(cmdstr, raiseonerr=False)
        if 'Added ID View' in cmd.stdout_text:
            print('View [%s] added successfully' % iview)
        else:
            pytest.fail("Failed to add View [%s]" % iview)

        cmdstr = ['ipa', 'idoverridegroup-add', iview,
                  group1 + '@' + ad1.domain.name]
        print("Running command : %s" % " ".join(cmdstr))
        cmd = multihost.master.run_command(cmdstr, raiseonerr=False)
        if 'Added Group ID override' in cmd.stdout_text:
            print('Group ID override added successfully')
        else:
            pytest.fail("Group ID override failed")

        cmdstr = ['ipa', 'idview-apply', iview, '--hosts', master1.hostname]
        print("Running command : %s" % " ".join(cmdstr))
        cmd = multihost.master.run_command(cmdstr, raiseonerr=False)
        if 'Number of hosts the ID View was applied to: 1' in cmd.stdout_text:
            print('ID View applied to host')
        else:
            pytest.fail("ID View applied to host failed")

        cmdstr = ['ipa', 'idoverridegroup-add', iview,
                  group2 + '@' + ad1.domain.name, '--group-name', group1]
        print("Running command : %s" % " ".join(cmdstr))
        cmd = multihost.master.run_command(cmdstr, raiseonerr=False)

        if 'Added Group ID override' in cmd.stdout_text:
            print('Group ID override added successfully')
        else:
            pytest.fail("Group ID override failed")

        service_control(multihost.master, 'sssd', 'stop')
        cmd = multihost.master.run_command(
            'rm -frv /var/lib/sss/{db,mc}/*', raiseonerr=False)
        service_control(multihost.master, 'sssd', 'start')

        cmdstr = ['id', user1 + '@' + ad1.domain.name]
        print("Running command : %s" % " ".join(cmdstr))
        cmd = master1.run_command(cmdstr, raiseonerr=False)
        if group2 + "@" + ad1.domain.name.lower() in cmd.stdout_text:
            print('Overridegroup is listed in id command')
        else:
            pytest.fail("idoverride group is not displayed")

    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Class teardown for IPA winsync migrate")
