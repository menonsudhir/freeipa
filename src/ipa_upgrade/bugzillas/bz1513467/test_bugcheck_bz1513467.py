"""
This is a quick test for bugzilla verification for bz1513467
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

    def test_bz1513467_0001(self, multihost):
        """
        Automation for bugzilla bz1513467
        https://bugzilla.redhat.com/show_bug.cgi?id=1513467#c12
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
        osver = multihost.master.get_os_version()
        print(osver)
        if osver >= '80':
            print("installing through dnf")
            cmd = ['dnf', '-y', 'module', 'install', master.config.server_module]
            master.qerun(cmd, exp_returncode=0)
            print_time()
        else:
            print("installing through yum")
            master.yum_install(['ipa-server', 'ipa-server-dns',
                                'bind-dyndb-ldap', 'bind-pkcs11',
                                'bind-pkcs11-utils'])
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
        #Checking Plugin for Replication before upgrade
        search = ['ldapsearch', '-xLLL',
                  '-D', multihost.master.config.dirman_id,
                  '-w', multihost.master.config.dirman_pw,
                  '-h', multihost.master.hostname,
                  '-b', 'cn=plugins,cn=config']
        string = 'Legacy Replication Plugin'

        cmd = multihost.master.run_command(search, raiseonerr=False)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        if string in cmd.stdout_text:
            print("Replication plugin found as expected")
        else:
            pytest.xfail("Replication plugin not found, kindly debug")

    def test_bz1513467_0002(self, multihost):
        """
        test for automation of upgradation of packeges
        test for rpm comparison
        """
        rpm = "ipa-server"
        print("Current IPA version")
        ipa_version = get_rpm_version(multihost.master, rpm)

        print(ipa_version)

        # get current ipa version
        upgrade_from = '7.3.b'
        upgrade_to = '7.5'
        print("Upgrading from : %s" % upgrade_from)
        print("Upgrading to : %s" % upgrade_to)

        if is_allowed_to_update(upgrade_to, upgrade_from):
            for repo in repo_urls[upgrade_to]:
                print("Upgrading using repo : %s" % repo)
                add_repo(multihost.master, repo)
        else:
            pytest.xfail("Please specify correct upgrade path")


        cmd = upgrade(multihost.master)   # upgrade starts at this point
        print(cmd.stdout_text)

        rpm = "ipa-server"
        updated_version = get_rpm_version(multihost.master, rpm)      # get updated ipa version
        print("Upgraded version is %s " % updated_version)             # prints upgraded version

        str1 = 'The ipa-server-upgrade command was successful'
        log2 = multihost.master.run_command(['tail', paths.IPAUPGRADELOGFILE], raiseonerr=False)
        print(log2.stdout_text)
        if str1 in log2.stdout_text:
            print("Upgraded Successfully")
        else:
            print("Upgrade failed")
            pytest.fail("Log test failed")

    def test_bz1513467_0003(self, multihost):
        """
        test for automation of upgradation of packeges
        test for service verification
        """
        multihost.master.kinit_as_admin()
        check_ipactl = multihost.master.run_command('ipactl status | grep RUNNING')
        if check_ipactl.returncode != 0:
            pytest.fail("IPA server service not RUNNING.Kindly debug")
        else:
            print("IPA service is running, continuing")

    def test_bz1513467_0004(self, multihost):
        """
        test bugzilla testing after upgrade
        """
        search = ['ldapsearch', '-xLLL',
                  '-D', multihost.master.config.dirman_id,
                  '-w', multihost.master.config.dirman_pw,
                  '-h', multihost.master.hostname,
                  '-b', 'cn=plugins,cn=config']
        string = 'Legacy Replication Plugin'

        cmd = multihost.master.run_command(search, raiseonerr=False)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        if string not in cmd.stdout_text:
            print("Replication plugin not found, expected. BZ1513467 verified successfully")
        else:
            pytest.fail("Replication plugin found, not expected. BZ1513467 verification failed")

    def class_teardown(self, multihost):
        """Full suite teardown """
        uninstall_server(multihost.master)
        pass
