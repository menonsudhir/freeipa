"""
This is a quick test for bugzilla verification for bz1477367
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

    def test_bz1477367_0001(self, multihost):
        """
        Automation for bugzilla bz1477367
        https://bugzilla.redhat.com/show_bug.cgi?id=1477367#c38
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
        master.yum_install(['ipa-server', 'ipa-server-dns',
                        'bind-dyndb-ldap', 'bind-pkcs11',
                        'bind-pkcs11-utils'])

        print_time()

        setup_master(multihost.master)

        ipa_version = get_rpm_version(multihost.master, 'ipa-server')
        print(ipa_version)

        print("\n IPA Server Before Updation")

        # checking for ipactl command output before updation
        multihost.master.kinit_as_admin()
        check5 = multihost.master.run_command('ipactl status | grep RUNNING')
        if check5.returncode != 0:
            print("IPA server service not RUNNING.Kindly debug")
        else:
            print("IPA service is running, continuing")

        #Diabling IPv6
        str1 = 'inet6'
        cmd = multihost.master.run_command('ip addr | grep inet6',
                                           raiseonerr=False)
        if str1 in cmd.stdout_text:
            print("IPV6 not disabled")

        file1 = '/etc/sysctl.conf'
        content1 = 'net.ipv6.conf.all.disable_ipv6 = 1'
        multihost.master.put_file_contents(file1, content1)
        cmd = multihost.master.run_command(['cat', file1],
                                           raiseonerr=False)

        print(cmd.stdout_text)
        cmd = multihost.master.run_command('sysctl -p',
                                           raiseonerr=False)
        if cmd.returncode == 0:
            print("sysctl command ran Successfully")
        else:
            print("sysctl did not run successfully")

        cmd = multihost.master.run_command('ip addr | grep inet6',
                                           raiseonerr=False)
        print(cmd.stdout_text)
        if str1 in cmd.stdout_text:
            pytest.fail("IPV6 not disabled")
        else:
            print("IPv6 Disabled Successfully.")

    def test_bz1477367_0002(self, multihost):
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


        cmd = upgrade(multihost.master)    # upgrade starts at this point
        print(cmd.stdout_text)

        rpm = "ipa-server"
        str1 = 'The ipa-server-upgrade command was successful'
        str2 = 'ERROR IPv6 stack is enabled in the kernel but there is no interface'
        log2 = multihost.master.run_command(['tail', paths.IPAUPGRADELOGFILE], raiseonerr=False)
        print(log2.stdout_text)
        if str1 not in log2.stdout_text and str2 in log2.stdout_text:
            print("Expected upgrade to fail, BZ1477367 verified")
        else:
            pytest.xfail("Bz1477367 verification test failed")

    def class_teardown(self, multihost):
        """Full suite teardown """
        uninstall_server(multihost.master)
        pass
