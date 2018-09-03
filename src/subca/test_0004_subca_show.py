"""
Testsuite for IPA Lightweight Sub CA - ca-show
"""
from ipa_pytests.shared.ca_utils import ca_add, ca_show, ca_del
from ipa_pytests.subca.lib import check_ca_add_output, check_ca_show_output, check_ca_del_output


class TestSubCAShow(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nUsing following hosts for IPA Lightweight Sub-CA testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("REPLICA: %s" % multihost.replica.hostname)
        print("*" * 80)
        multihost.realm = multihost.master.domain.realm

    def test_0001_subca_show_help(self, multihost):
        """
        :Title: IDM-IPA-TC: ipa ca show help

        :Requirement: IDM-IPA-REQ : Lightweight sub-CAs

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        cmd = "ipa help ca-show"
        print("Running : {0}".format(cmd))
        cmdout = multihost.master.run_command(cmd, raiseonerr=False)
        assert "Usage: ipa [global-options] " \
               "ca-show NAME [options]" in cmdout.stdout_text
        assert "Display the properties of a CA." in cmdout.stdout_text

        cmd = "ipa ca-show --help"
        print("Running : {0}".format(cmd))
        cmdout = multihost.master.run_command(cmd, raiseonerr=False)
        assert "Usage: ipa [global-options] " \
               "ca-show NAME [options]" in cmdout.stdout_text
        assert "Display the properties of a CA." in cmdout.stdout_text

    def test_0002_subca_show(self, multihost):
        """
        :Title: IDM-IPA-TC: ipa ca show for existing Sub CA

        :Requirement: IDM-IPA-REQ : Lightweight sub-CAs

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0002_subca1"
        subca['realm'] = multihost.realm

        cmd = ca_add(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_add_output(subca, cmd[1])

        cmd = ca_show(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_show_output(subca, cmd[1])
        # Delete create Sub CA
        cmd = ca_del(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_del_output(subca, cmd[1])

    def test_0003_subca_show_replica(self, multihost):
        """
        :Title: IDM-IPA-TC: ipa ca show for existing Sub CA from IPA Replica Server

        :Requirement: IDM-IPA-REQ : Lightweight sub-CAs

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.replica.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0003_subca1"
        subca['realm'] = multihost.realm
        # Add Sub CA on replica
        cmd = ca_add(multihost.replica, subca)
        if cmd[0] == 0:
            check_ca_add_output(subca, cmd[1])

        # Show Sub CA
        cmd = ca_show(multihost.replica, subca)
        if cmd[0] == 0:
            check_ca_show_output(subca, cmd[1])
        # Delete create Sub CA
        cmd = ca_del(multihost.replica, subca)
        if cmd[0] == 0:
            check_ca_del_output(subca, cmd[1])

    def test_0004_subca_show(self, multihost):
        """
        :Title: IDM-IPA-TC: ipa ca show for non-existing Sub CA

        :Requirement: IDM-IPA-REQ : Lightweight sub-CAs

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0004_subca1"
        cmd = ca_show(multihost.master, subca)
        assert "{0}: Certificate Authority " \
               "not found".format(subca['name']) in cmd[2]

    def test_0005_subca_show_replica(self, multihost):
        """
        :Title: IDM-IPA-TC: ipa ca show for existing Sub CA from IPA Replica Server

        :Requirement: IDM-IPA-REQ : Lightweight sub-CAs

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.replica.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0005_subca1"

        cmd = ca_show(multihost.replica, subca)
        assert "{0}: Certificate Authority " \
               "not found".format(subca['name']) in cmd[2]

    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Class teardown for Sub CA")
