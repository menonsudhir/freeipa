"""
This is an upgrade test for BZ 1852244
Upgrade path: RHEL8.1 -> RHEL8.2 -> RHEL8.3
Initial system is RHEL 8.1
The system is then upgraded to RHEL 8.2 and ipa-healthcheck
command is run for sanity check
After that the system is upgraded to RHEL 8.3 and ipa-healthcheck
command is run for sanity check
"""

import time
import subprocess

import pytest

from ipa_pytests.ipa_upgrade.constants import repo_urls
from ipa_pytests.ipa_upgrade.utils import upgrade, modify_repo


class TestUpgradeHealthcheck(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        multihost.realm = multihost.master.domain.realm

        print("Using following hosts for IPA server Upgrade testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("*" * 80)

    def test_bz1852244_0001(self, multihost):
        """
        Automation for bugzilla BZ1852244
        https://bugzilla.redhat.com/show_bug.cgi?id=1852244
        """

        master = multihost.master
        replica = multihost.replica

        if master.transport.file_exists('/var/log/ipaserver-install.log'):
            result = master.run_command(
                ['tail',
                 '/var/log/ipaserver-install.log']
            )
            assert 'The ipa-server-install command was successful' in result.stdout_text

        if replica.transport.file_exists('/var/log/ipareplica-install.log'):
            result = replica.run_command(
                ['tail',
                 '/var/log/ipareplica-install.log']
            )
            assert 'The ipa-replica-install command was successful' in result.stdout_text

        # upgrade system from RHEL 8.1 to RHEL8.2
        repo_url = repo_urls["8.2.app"]
        modify_repo(master, 'rhelappstream82',
                    repo_url, '/etc/yum.repos.d/rhel-8.2-appstream.repo')
        modify_repo(replica, 'rhelappstream82',
                    repo_url, '/etc/yum.repos.d/rhel-8.2-appstream.repo')
        repo_url = repo_urls["8.2.base"]
        modify_repo(master, 'rhelbaseos82',
                    repo_url, '/etc/yum.repos.d/rhel-8.2-baseos.repo')
        modify_repo(replica, 'rhelbaseos82',
                    repo_url, '/etc/yum.repos.d/rhel-8.2-baseos.repo')

        cmd_output = master.run_command(['dnf', '-y', 'upgrade'])
        assert cmd_output.returncode == 0
        time.sleep(30)
        cmd_output = replica.run_command(['dnf', '-y', 'upgrade'])
        assert cmd_output.returncode == 0

        if master.transport.file_exists('/var/log/ipaupgrade.log'):
            result = master.run_command(
                ['tail',
                 '/var/log/ipaupgrade.log']
            )
            assert 'The ipa-server-upgrade command was successful' in result.stdout_text

        if replica.transport.file_exists('/var/log/ipaupgrade.log'):
            result = replica.run_command(
                ['tail',
                 '/var/log/ipaupgrade.log']
            )
            assert 'The ipa-server-upgrade command was successful' in result.stdout_text

        # allow the test to fail as ipa-healthcheck-core is installed by default and ipa-healthcheck is not
        try:
            cmd_output = master.run_command(['ipa-healthcheck', '--source',
                                             'ipahealthcheck.meta.services'])
        except subprocess.CalledProcessError:
            print("ipa-healthcheck command not present by default")

        # explicitly install ipa-healthcheck before RHEL 8.2 -> RHEL 8.3 upgrade
        # which will ensure ipa-healthcheck runs on RHEL 8.3
        cmd_output = master.run_command(['dnf', 'install', '-y', 'ipa-healthcheck-0.4'])
        assert cmd_output.returncode == 0
        cmd_output = replica.run_command(['dnf', 'install', '-y', 'ipa-healthcheck-0.4'])
        assert cmd_output.returncode == 0

        # set nightly repo to pull latest packages
        repo_url = repo_urls["8.3.app"]
        modify_repo(master, 'rhelappstream83',
                    repo_url, '/etc/yum.repos.d/rhel-8.3-appstream.repo')
        modify_repo(replica, 'rhelappstream83',
                    repo_url, '/etc/yum.repos.d/rhel-8.3-appstream.repo')
        repo_url = repo_urls["8.3.base"]
        modify_repo(master, 'rhelbaseos83',
                    repo_url, '/etc/yum.repos.d/rhel-8.3-baseos.repo')
        modify_repo(replica, 'rhelbaseos83',
                    repo_url, '/etc/yum.repos.d/rhel-8.3-baseos.repo')

        # Update the packages to latest version
        cmd_output = master.run_command(['dnf', '-y', 'upgrade'])
        assert cmd_output.returncode == 0
        time.sleep(30)
        cmd_output = replica.run_command(['dnf', '-y', 'upgrade'])
        assert cmd_output.returncode == 0

        if master.transport.file_exists('/var/log/ipaupgrade.log'):
            result = master.run_command(
                ['tail',
                 '/var/log/ipaupgrade.log']
            )
            assert 'The ipa-server-upgrade command was successful' in result.stdout_text

        if replica.transport.file_exists('/var/log/ipaupgrade.log'):
            result = replica.run_command(
                ['tail',
                 '/var/log/ipaupgrade.log']
            )
            assert 'The ipa-server-upgrade command was successful' in result.stdout_text

        cmd_output = master.run_command(['ipa-healthcheck', '--source', 'ipahealthcheck.meta.services'])
        assert cmd_output.returncode == 0
