import pytest
from ipa_pytests.shared.sudo_utils import sudorule_add, sudorule_mod, sudorule_add_option, sudorule_find, sudorule_del, \
    sudorule_add_allow_command, sudorule_add_deny_command, sudocmd_add, sudocmd_del
from ipa_pytests.shared.user_utils import add_ipa_user, del_ipa_user
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.utils import sssd_cache_reset
sudo_rule = "testrule"
ipa_user1 = "testuser1"
cmd_common_in_allow_and_deny_ls = "/usr/bin/ls"  # Hence, expected to be denied
cmd_only_in_allow_date = "/usr/bin/date"  # Hence, expected to be allowed


class TestSudoRule(object):
    """This test is to check whether a command is denied or allowed
    if it is common in both sudo deny and sudo allow aspect
    within a sudo rule"""

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: %s" % multihost.master.hostname)

    def test_sudorule_allow(self, multihost):
        """
        Title: IDM-IPA-TC: Sudo-Rule : To check for allow permission
        """
        # Adding user for environment set
        print("\nkinit as admin")
        multihost.master.kinit_as_admin()
        print("\nAdding ipa user %s to IDM" % ipa_user1)
        add_ipa_user(multihost.master, ipa_user1,
                     passwd=None, first='test', last='user')
        print("\nAdded ipa user %s to IDM\n" % ipa_user1)

        # Adding sudorule with option
        print("Adding sudorule %s " % sudo_rule)

        sudorule_add(
            multihost.master,
            sudo_rule,
            usercat='all',
            hostcat='all',
            cmdcat=None,
            runasusercat='all',
            runasgroupcat='all')

        print("Adding sudorule option !authenticate")
        sudorule_add_option(multihost.master, sudo_rule, '!authenticate')
        print("Added sudorule option !authenticate\n")

        # Setting sudorule order
        print("Setting sudo order to 13")
        sudorule_mod(multihost.master, sudo_rule, order=13)

        print("\nkinit as admin")
        multihost.master.kinit_as_admin()

        print("Adding sudocmds to IDM:\n")
        sudocmd_add(multihost.master, cmd_only_in_allow_date)

        print("Adding sudorule allow command %s " % cmd_only_in_allow_date)
        sudorule_add_allow_command(
            multihost.master, sudo_rule, sudocmds=cmd_only_in_allow_date)

        sssd_cache_reset(multihost.master)
        print("SSSD cache reset done\n")

        cmd_sudocmd_allowed_query = "su -c 'sudo %s' %s " % (
            cmd_only_in_allow_date, ipa_user1)
        print("Running command: %s" % cmd_sudocmd_allowed_query)

        op_sudocmd_allowed_query = multihost.master.run_command(
            cmd_sudocmd_allowed_query)
        # assert op_sudocmd_allowed_query.returncode == 0
        print("CORRECT ACCESS:Allowed OBSERVED!\n")
        print("STDOUT is : %s\n" % op_sudocmd_allowed_query.stdout_text)

    def test_sudorule_allow_and_deny(self, multihost):
        """
        :Title: IDM-IPA-TC: Sudo-Rule : to check for conflict in allow and deny permission
        """
        print("kinit as admin")
        multihost.master.kinit_as_admin()

        print("Adding sudocmds to IDM:\n")
        sudocmd_add(multihost.master, cmd_common_in_allow_and_deny_ls)

        print("Adding sudorule allow command %s " %
              cmd_common_in_allow_and_deny_ls)
        sudorule_add_allow_command(
            multihost.master,
            sudo_rule,
            sudocmds=cmd_common_in_allow_and_deny_ls)

        print("Adding sudorule deny command %s" %
              cmd_common_in_allow_and_deny_ls)
        sudorule_add_deny_command(
            multihost.master,
            sudo_rule,
            sudocmds=cmd_common_in_allow_and_deny_ls)

        print("Resetting sssd cache")
        sssd_cache_reset(multihost.master)
        print("SSSD cache reset done\n")

        cmd_sudocmd_denied_query = "su -c 'sudo %s' %s" % (
            cmd_common_in_allow_and_deny_ls, ipa_user1)
        print("Running command: %s\n" % cmd_sudocmd_denied_query)

        op_sudocmd_denied_query = multihost.master.run_command(
            cmd_sudocmd_denied_query, raiseonerr=False)
        assert op_sudocmd_denied_query.returncode != 0
        print(
            "Sudocommand %s is in both allowed and denied, hence it is denied.\nCORRECT ACCESS:Denied OBSERVED!\n" %
            cmd_common_in_allow_and_deny_ls)
        print("STDERR is : %s\n" % op_sudocmd_denied_query.stderr_text)

    def class_teardown(self, multihost):
        """ Full suite teardown"""
        print("\ndeleting sudorule %s from the IDM" % sudo_rule)
        sudorule_del(multihost.master, sudo_rule)
        print("sudorule %s successfully deleted\n" % sudo_rule)

        print("deleting sudo commands from IDM")
        sudocmd_del(multihost.master, cmd_common_in_allow_and_deny_ls)
        sudocmd_del(multihost.master, cmd_only_in_allow_date)
        print("sudo commands %s %s successfully deleted\n" %
              (cmd_common_in_allow_and_deny_ls, cmd_only_in_allow_date))

        print("deleting ipa user from IDM")
        del_ipa_user(multihost.master, ipa_user1)

        print("\nDestroying kerberos tickets")
        multihost.master.run_command("kdestroy -A")
        print("kerberos tickets destroyed")
