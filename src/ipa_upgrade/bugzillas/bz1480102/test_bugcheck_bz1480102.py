"""
This is a quick test for bugzilla verification for bz1480102
"""
import time
import pytest
from ipa_pytests.shared.rpm_utils import list_rpms
from ipa_pytests.qe_install import disable_firewall, set_hostname, set_etc_hosts, set_rngd, print_time
from ipa_pytests.shared import paths
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.utils import ipa_version_gte
from ipa_pytests.shared.rpm_utils import get_rpm_version
from ipa_pytests.ipa_upgrade.utils import is_allowed_to_update, upgrade
from ipa_pytests.ipa_upgrade.constants import repo_urls
from ipa_pytests.shared.yum_utils import add_repo
from ipa_pytests.qe_install import uninstall_server, setup_replica, setup_master


class TestBugzilla(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        multihost.realm = multihost.master.domain.realm

        print("Using following hosts for IPA server Upgrade testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("*" * 80)

    def test_bz1480102_0001(self, multihost):
        """
        Setup for bugzilla bz1480102
        https://bugzilla.redhat.com/show_bug.cgi?id=1480102#c25
        """

        master = multihost.master
        upgrade_from = '7.3.b'
        if upgrade_from != '7.3.b':
            pytest.fail("Upgrade from should be Rhel 7.3.z")
        # upgrade_from this can be used to set repo version of packages
        # for this refer ipa_upgrade/constants.py

        for repo in repo_urls[upgrade_from]:
            add_repo(master, repo)

        print("Listing RPMS")
        list_rpms(master)
        print("Disabling Firewall")
        disable_firewall(master)
        print("Setting hostname")
        set_hostname(master)
        print("Setting /etc/hosts")
        set_etc_hosts(master)
        print("Setting up RNGD")
        set_rngd(master)

        print_time()
        print("Installing required packages")
        cmd = ['dnf', '-y', 'module', 'install', 'idm:4']
        master.qerun(cmd, exp_returncode=0)

        print_time()

        setup_master(multihost.master)

        ipa_version = get_rpm_version(multihost.master, 'ipa-server')
        print(ipa_version)

        print ("\n IPA Server Before Updation")

        # checking for ipactl command output before updation
        multihost.master.kinit_as_admin()
        check5 = multihost.master.run_command('ipactl status | grep RUNNING')
        if check5.returncode != 0:
            print("IPA server service not RUNNING.Kindly debug")
        else:
            print("IPA service is running, continuing")

        cn = 'cn=TESTRELM.TEST IPA CA,cn=certificates,cn=ipa,cn=etc,dc=testrelm,dc=test'
        username = 'cn=directory manager'
        password = 'Secret123'
        runcmd = ['ldapsearch', '-xLLL', '-D', username, '-w', password, '-b', cn, 'dn',
                  'ipaCertIssuerSerial']
        print(runcmd)

        # Check ldapsearch
        cmd = multihost.master.run_command(runcmd, raiseonerr=False)
        exp_output = 'ipaCertIssuerSerial'
        print(cmd.stdout_text)
        if exp_output in cmd.stdout_text:
            print("String Found")

        # Create LDIF file for import
        ldif_entry = ("dn: cn=TESTRELM.TEST IPA CA,cn=certificates,cn=ipa,cn=etc,dc=testrelm,dc=test\n"
                      "changetype: modrdn\n"
                      "newrdn: cn=CA 1\n"
                      "deleteoldrdn: 1")

        multihost.master.put_file_contents('/tmp/modrdn.ldif', ldif_entry)

        # Import LDIF file
        runcmd = ['ldapmodify', '-D', username, '-w', password, '-f', '/tmp/modrdn.ldif']
        print(runcmd)
        cmd = multihost.master.run_command(runcmd, raiseonerr=False)

        # Check if LDIF imported correctly
        cn = 'cn=CA 1,cn=certificates,cn=ipa,cn=etc,dc=testrelm,dc=test'
        runcmd = ['ldapsearch', '-xLLL', '-D', username, '-w', password, '-b', cn, 'dn',
                  'ipaCertIssuerSerial']
        print(runcmd)

        #Check ldap search
        cmd = multihost.master.run_command(runcmd, raiseonerr=False)
        exp_output = 'CA 1'
        print(cmd.stdout_text)
        if exp_output in cmd.stdout_text:
            print("String Found after ldapmodify")

    def test_bz1480102_0002(self, multihost):
        """
        IDM-IPA-TC : IPA Upgrade : Verification for bugzilla bz1480102 after upgrade
        """
        rpm = "ipa-server"
        print("Current IPA version")
        ipa_version = get_rpm_version(multihost.master, rpm)

        print(ipa_version)

        # get current ipa version before upgrade
        upgrade_from = '7.3.b'
        upgrade_to = '7.5.a'
        print("Upgrading from : %s" % upgrade_from)
        print("Upgrading to : %s" % upgrade_to)

        if is_allowed_to_update(upgrade_to, upgrade_from):
            for repo in repo_urls[upgrade_to]:
                print("Upgrading using repo : %s" % repo)
                add_repo(multihost.master, repo)
        else:
            pytest.xfail("Please specify correct upgrade path")

        # Upgrade IPA
        cmd = upgrade(multihost.master)    # upgrade starts at this point
        print(cmd.stdout_text)

        # Verify Upgrade
        rpm = "ipa-server"
        str1 = 'The ipa-server-upgrade command was successful'
        log2 = multihost.master.run_command(['tail', paths.IPAUPGRADELOGFILE], raiseonerr=False)
        print(log2.stdout_text)
        if str1 in log2.stdout_text:
            print("Upgrade Successful, Proceeding")
        else:
            pytest.xfail("Upgrade Failed")

        # get current ipa version after upgrade
        rpm = "ipa-server"
        print("Current IPA version")
        ipa_version = get_rpm_version(multihost.master, rpm)
        print(ipa_version)

        # checking for ipactl command output after updation
        multihost.master.kinit_as_admin()
        check5 = multihost.master.run_command('ipactl status | grep RUNNING')
        if check5.returncode != 0:
            print("IPA server service not RUNNING.Kindly debug")
        else:
            print("IPA service is running, continuing")

        # Verify Bugzilla bz1480102
        cn = 'cn=TESTRELM.TEST IPA CA,cn=certificates,cn=ipa,cn=etc,dc=testrelm,dc=test'
        username = 'cn=directory manager'
        password = 'Secret123'
        runcmd = ['ldapsearch', '-xLLL', '-D', username, '-w', password, '-b', cn, 'dn',
                  'ipaCertIssuerSerial']
        print(runcmd)
        cmd = multihost.master.run_command(runcmd, raiseonerr=False)
        exp_output = 'IPA CA'
        print(cmd.stdout_text)
        if exp_output in cmd.stdout_text:
            print("String Found, thus Bz1480102 Verified")
        else:
            pytest.xfail("String not found, BZ1480102 verification Failed")

    def class_teardown(self, multihost):
        """Full suite teardown """
        uninstall_server(multihost.master)
        pass
