import pytest
from ipa_pytests.shared.sudo_utils import sudorule_add, sudorule_mod, sudorule_add_option, sudorule_find, sudorule_del, \
    sudorule_add_allow_command, sudorule_add_deny_command, sudocmd_add, sudocmd_del
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.utils import sssd_cache_reset

rulename = "testrule"
command_common_in_allow_and_deny = "/usr/bin/ls"  # Hence, expected to be denied
command_only_in_allow = "/usr/bin/date"  # Hence it is expected to be allowed


class TestSudoRule(object):
    """This test is to check whether a command is denied or allowed
    if it is common in both sudo deny and sudo allow aspect
    within a sudo rule"""

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print"MASTER: ", multihost.master.hostname

    def test_adding_sudorule(self, multihost):
        """
        Title: IDM-IPA-TC: Sudo-Rule : Adding Rule
        """
        print("Adding sudorule {}".format(rulename))
        sudorule_add(multihost.master, rulename, usercat='all',
                     hostcat='all', cmdcat=None, runasusercat='all', runasgroupcat='all')

        print("Adding sudorule option !authenticate")
        sudorule_add_option(multihost.master, rulename, '!authenticate')
        print("Added sudorule option !authenticate\n")

    def test_sudorule_allow(self, multihost):
        """
        Title: IDM-IPA-TC: Sudo-Rule : To check for allow permission
        """
        print("\nkinit as admin")
        multihost.master.kinit_as_admin()

        print("Adding sudocmds to IDM:\n")
        sudocmd_add(multihost.master, command_only_in_allow)

        print("Adding sudorule allow command {}".format(command_only_in_allow))
        sudorule_add_allow_command(
            multihost.master, rulename, sudocmds=command_only_in_allow)

        sssd_cache_reset(multihost.master)
        print("SSSD cache reset done\n")

        cmd_sudocmd_allowed_query = "su -c 'sudo {}' testuser1".format(
            command_only_in_allow)
        print("Running command: {}".format(cmd_sudocmd_allowed_query))

        op_sudocmd_allowed_query = multihost.master.run_command(
            cmd_sudocmd_allowed_query)
        assert op_sudocmd_allowed_query.returncode == 0
        print("CORRECT ACCESS:Allowed OBSERVED!\n")
        print("STDOUT is : {}\n".format(
            op_sudocmd_allowed_query.stdout_text))

    def test_sudorule_allow_and_deny(self, multihost):
        """
        :Title: IDM-IPA-TC: Sudo-Rule : to check for conflict in allow and deny permission
        """
        print("kinit as admin")
        multihost.master.kinit_as_admin()

        print("Adding sudocmds to IDM:\n")
        sudocmd_add(multihost.master, command_common_in_allow_and_deny)

        print("Adding sudorule allow command {}".format(
            command_common_in_allow_and_deny))
        sudorule_add_allow_command(
            multihost.master, rulename, sudocmds=command_common_in_allow_and_deny)

        print("Adding sudorule deny command {}".format(
            command_common_in_allow_and_deny))
        sudorule_add_deny_command(
            multihost.master, rulename, sudocmds=command_common_in_allow_and_deny)

        print("Resetting sssd cache")
        sssd_cache_reset(multihost.master)
        print("SSSD cache reset done\n")

        cmd_sudocmd_denied_query = "su -c 'sudo {}' testuser1".format(
            command_common_in_allow_and_deny)
        print("Running command: {}\n".format(cmd_sudocmd_denied_query))

        op_sudocmd_denied_query = multihost.master.run_command(
            cmd_sudocmd_denied_query, raiseonerr=False)
        assert op_sudocmd_denied_query.returncode != 0
        print("Sudocommand {} is in both allowed and denied, therefore, {} is denied.\nCORRECT ACCESS:Denied OBSERVED!\n".format(
            command_common_in_allow_and_deny, command_common_in_allow_and_deny))
        print("STDERR is : {}\n".format(
            op_sudocmd_denied_query.stderr_text))

    def class_teardown(self, multihost):
        """ Full suite teardown"""
        print("\ndeleting sudorule {} from the IDM\n".format(rulename))
        sudorule_del(multihost.master, rulename)
        print("sudorule {} successfully deleted\n".format(rulename))

        print("deleting sudo commands from IDM")
        sudocmd_del(multihost.master, command_common_in_allow_and_deny)
        sudocmd_del(multihost.master, command_only_in_allow)
        print("sudo commands {} {} successfully deleted\n".format(
            command_common_in_allow_and_deny, command_only_in_allow))
