"""
Testsuite for IPA Lightweight Sub CA - ca-del
"""
from ipa_pytests.shared.ca_utils import ca_add, ca_find, ca_del
from ipa_pytests.subca.lib import check_ca_find_output, check_ca_add_output, check_ca_del_output


class TestSubCADel(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nUsing following hosts for IPA Lightweight Sub-CA testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("REPLICA: %s" % multihost.replica.hostname)
        print("*" * 80)
        multihost.replica = multihost.replicas[0]
        multihost.realm = multihost.master.domain.realm

    def test_0001_subca_del_help(self, multihost):
        """
        :Title: IDM-IPA-TC: ipa ca delete with help option

        :Requirement: IDM-IPA-REQ : Lightweight sub-CAs

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        cmd = "ipa help ca-del"
        print("Running : {0}".format(cmd))
        cmdout = multihost.master.run_command(cmd, raiseonerr=False)
        assert "Usage: ipa [global-options] " \
               "ca-del NAME... [options]" in cmdout.stdout_text
        assert "Delete a CA" in cmdout.stdout_text
        cmd = "ipa ca-del --help"
        print("Running : {0}".format(cmd))
        cmdout = multihost.master.run_command(cmd, raiseonerr=False)
        assert "Usage: ipa [global-options] " \
               "ca-del NAME... [options]" in cmdout.stdout_text
        assert "Delete a CA." in cmdout.stdout_text

    def test_0002_subca_del_subca(self, multihost):
        """
        :Title: IDM-IPA-TC: ipa ca delete with non-interactive mode
        :Requirement: IDM-IPA-REQ : Lightweight sub-CAs

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0002_subca1"
        subca['realm'] = multihost.realm
        # Add Sub CA
        cmd = ca_add(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_add_output(subca, cmd[1])
        # Check if Sub CA is actually created or not
        cmd = ca_find(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_find_output(subca, cmd[1])
        # Delete create Sub CA
        cmd = ca_del(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_del_output(subca, cmd[1])

    def test_0003_subca_del_interactive(self, multihost):
        """
        :Title:  IDM-IPA-TC: ipa ca delete with interactive mode

        :Requirement: IDM-IPA-REQ : Lightweight sub-CAs

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0003_subca_1"
        subca['realm'] = multihost.realm

        # Add Sub CA
        cmd = "ipa ca-add"
        print("Running : {0}".format(cmd))
        expect_script = 'set timeout 15\n'
        expect_script += 'spawn {0}\n'.format(cmd)
        expect_script += 'expect "Name: "\n'
        expect_script += 'send "%s\r"\n' % subca['name']
        expect_script += 'expect "Subject DN: "\n'
        subject_dn = "CN={0},O={1}\n".format(subca['name'], subca['realm'])
        expect_script += 'send "%s\r"\n' % subject_dn
        expect_script += 'expect EOF\n'
        output = multihost.master.expect(expect_script)
        check_ca_add_output(subca, output.stdout_text)
        # Delete create Sub CA
        cmd = "ipa ca-del"
        print("Running : {0}".format(cmd))
        expect_script = 'set timeout 15\n'
        expect_script += 'spawn {0}\n'.format(cmd)
        expect_script += 'expect "Name: "\n'
        expect_script += 'send "%s\r"\n' % subca['name']
        expect_script += 'expect EOF\n'
        output = multihost.master.expect(expect_script)
        assert "Deleted CA \"{0}\"".format(subca['name']) in output.stdout_text

    def test_0004_subca_del_non_existing_subca(self, multihost):
        """
        :Title: IDM-IPA-TC: ipa ca delete with non-existent Sub CA

        :Requirement: IDM-IPA-REQ : Lightweight sub-CAs

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0004_subca1"
        subca['realm'] = multihost.realm
        # Delete non-existing Sub CA
        cmd = ca_del(multihost.master, subca)
        print("Stderr: %s " % cmd[2])
        assert "ipa: ERROR: no such entry" in cmd[2]

    def test_0005_subca_del_default_subca(self, multihost):
        """
        :Title: IDM-IPA-TC: ipa ca delete with default Sub CA

        :Requirement: IDM-IPA-REQ : Lightweight sub-CAs

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        subca = {}
        subca['name'] = "ipa"
        subca['realm'] = multihost.realm
        subca['cname'] = "Certificate Authority"

        # Find existing IPA Default Sub CA
        cmd = ca_find(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_find_output(subca, cmd[1])

        # Delete default Sub CA
        cmd = ca_del(multihost.master, subca)
        assert "CA ipa cannot be deleted/modified: " \
               "IPA CA cannot be deleted" in cmd[2]

    def test_0006_subca_del_multiple_subca(self, multihost):
        """
        :Title: IDM-IPA-TC: ipa ca delete multiple Sub CAs

        :Requirement: IDM-IPA-REQ : Lightweight sub-CAs

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        subca_prefix = "test_0006_subca_"
        subca_list = []
        for i in range(1, 20):
            subca = {}
            subca['name'] = "{0}{1}".format(subca_prefix, i)
            subca['realm'] = multihost.realm

            subca_list.append(subca['name'])
            cmd = ca_add(multihost.master, subca)

        # Delete all Sub CA
        subca = {}
        subca['name'] = " ".join(subca_list)
        cmd = ca_del(multihost.master, subca)
        subca['name'] = ",".join(subca_list)
        assert "Deleted CA \"{0}\"".format(subca['name']) in cmd[1]

    def test_0007_subca_del_replica_subca(self, multihost):
        """
        :Title: IDM-IPA-TC: ipa ca delete multiple Sub CAs from replica

        :Requirement: IDM-IPA-REQ : Lightweight sub-CAs

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.replica.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0007_subca1"
        subca['realm'] = multihost.realm
        # Add Sub CA
        cmd = ca_add(multihost.replica, subca)
        if cmd[0] == 0:
            check_ca_add_output(subca, cmd[1])

        # Check if Sub CA is actually created or not
        cmd = ca_find(multihost.replica, subca)
        if cmd[0] == 0:
            check_ca_find_output(subca, cmd[1])
        # Delete create Sub CA
        cmd = ca_del(multihost.replica, subca)
        if cmd[0] == 0:
            check_ca_del_output(subca, cmd[1])

    def test_0008_subca_del_multiple_subca_replica(self, multihost):
        """
        :Title: IDM-IPA-TC: ipa ca delete multiple Sub CAs from Replica

        :Requirement: IDM-IPA-REQ : Lightweight sub-CAs

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.replica.kinit_as_admin()
        subca_prefix = "test_0008_subca_"
        subca_list = []
        for i in range(1, 20):
            subca = {}
            subca['name'] = "{0}{1}".format(subca_prefix, i)
            subca['realm'] = multihost.realm
            subca_list.append(subca['name'])

            cmd = ca_add(multihost.replica, subca)

        subca = {}
        subca['name'] = " ".join(subca_list)
        cmd = ca_del(multihost.replica, subca)
        subca['name'] = ",".join(subca_list)
        check_ca_del_output(subca, cmd[1])

    def test_0009_subca_del_non_existing_subca_replica(self, multihost):
        """
        :Title: IDM-IPA-TC: ipa ca delete with non-existent Sub CA from replica

        :Requirement: IDM-IPA-REQ : Lightweight sub-CAs

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.replica.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0009_subca1"
        # Delete non-existing Sub CA from replica
        cmd = ca_del(multihost.master, subca)
        print("Stderr: %s " % cmd[2])
        assert "ipa: ERROR: no such entry" in cmd[2]

    def test_0010_subca_del_default_subca_replica(self, multihost):
        """
        :Title: IDM-IPA-TC: ipa ca delete with default Sub CA from IPA replica

        :Requirement: IDM-IPA-REQ : Lightweight sub-CAs

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.replica.kinit_as_admin()
        subca = {}
        subca['name'] = "ipa"
        subca['cname'] = 'Certificate Authority'
        subca['realm'] = multihost.realm

        # Delete default Sub CA from replica
        cmd = ca_del(multihost.replica, subca)
        assert "CA ipa cannot be deleted/modified: " \
               "IPA CA cannot be deleted" in cmd[2]

    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Class teardown for Sub CA")
