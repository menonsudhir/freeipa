"""
This is a quick test for bugzilla verification for bz1680039
"""
from ipa_pytests.qe_class import multihost
from ipa_pytests.ipa_upgrade.utils import upgrade, modify_repo
from ipa_pytests.shared import paths
from ipa_pytests.ipa_upgrade.constants import repo_urls
from ipa_pytests.qe_install import uninstall_server


class TestBugzilla(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """

        print("Using following hosts for IPA server Upgrade testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("*" * 80)

    def test_missing_certmonger_CA_bz1680039(self, multihost):
        """Test to check if error thrown when certmonger CA is missing

        If certmonger CA is not present it used to throw ambigious
        message. With the fix, it now point to the proper issue

        https://bugzilla.redhat.com/show_bug.cgi?id=1680039
        """

        master = multihost.master

        # set nightly repo to pull latest packages
        repo_url = repo_urls["8.2.app.nightly"]
        modify_repo(master, 'rhelappstream',
                    repo_url, '/etc/yum.repos.d/rhel-8.2-appstream.repo')
        repo_url = repo_urls["8.2.base.nightly"]
        modify_repo(master, 'rhelbaseos',
                    repo_url, '/etc/yum.repos.d/rhel-8.2-baseos.repo')

        # remove a CA configuration from certmonger
        cmd_arg = ['getcert', 'remove-ca', '-c', 'dogtag-ipa-ca-renew-agent']
        master.run_command(cmd_arg)

        # Update the packages to latest version
        upgrade(master)

        err_msg = ("ERROR certmonger CA 'dogtag-ipa-ca-renew-agent'"
                   " is not defined")
        log_check = master.run_command(['tail', paths.IPAUPGRADELOGFILE],
                                       raiseonerr=False)
        assert err_msg in log_check.stdout_text

        master.run_command(['ipa-server-upgrade'], raiseonerr=False)
        log_check = master.run_command(['tail', paths.IPAUPGRADELOGFILE],
                                       raiseonerr=False)
        assert err_msg in log_check.stdout_text

    def class_teardown(self, multihost):
        """Full suite teardown """
        uninstall_server(multihost.master)
        pass
