"""
Testsuite for IPA Lightweight Sub CA - ca-del
"""
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.ca_utils import *
from lib import *
import pexpect
import pytest


class TestSubCADel(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nUsing following hosts for IPA Lightweight Sub-CA testcases")
        print("*" * 80)
        multihost.replica = multihost.replicas[0]
        print("MASTER: %s" % multihost.master.hostname)
        print("REPLICA: %s" % multihost.replica.hostname)
        print("*" * 80)

    def test_0001_subca_del_help(self, multihost):
        """
        test_0001_subca_del_help
        IDM-IPA-TC: ipa ca del with help option
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
        test_0002_subca_del_subca
        IDM-IPA-TC: ipa ca delete with non-interactive mode
        """
        multihost.master.kinit_as_admin()
        domain = multihost.master.domain.name.upper()
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
        test_0003_subca_del_interactive
        IDM-IPA-TC: ipa ca delete with interactive mode
        """
        multihost.master.kinit_as_admin()
        domain = multihost.master.domain.name.upper()
        subca = {}
        subca['name'] = "test_0003_subca_1"
        subca['realm'] = multihost.realm

        # Add Sub CA
        cmd = "ipa ca-add"
        print("Running : {0}".format(cmd))
        events = {"Name: ": '{0}\n'.format(subca['name']),
                  "Subject DN: ": "CN={0},O={1}\n".format(subca['name'],
                                                          subca['realm'])}
        cmdout = pexpect.run(cmd, events=events)
        check_ca_add_output(subca, cmdout)
        # Delete create Sub CA
        cmd = "ipa ca-del"
        print("Running : {0}".format(cmd))
        events = {"Name: ": '{0}\n'.format(subca['name'])}
        cmdout = pexpect.run(cmd, events=events)
        assert "Deleted CA \"{0}\"".format(subca['name']) in cmdout

    def test_0004_subca_del_non_existing_subca(self, multihost):
        """
        test_0004_subca_del_non_existing_subca
        IDM-IPA-TC: ipa ca delete with non-existent Sub CA
        """
        multihost.master.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0004_subca1"
        subca['realm'] = multihost.realm

        # Delete non-existing Sub CA
        cmd = ca_del(multihost.master, subca)
        assert "{0}: Certificate Authority " \
               "not found".format(subca['name']) in cmd[2]

    def test_0005_subca_del_default_subca(self, multihost):
        """
        test_0005_subca_del_default_subca
        IDM-IPA-TC: ipa ca delete with default Sub CA
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
        test_0006_subca_del_multiple_subca
        IDM-IPA-TC: ipa ca delete multiple Sub CAs
        """
        multihost.master.kinit_as_admin()
        subca_prefix = "test_0006_subca_"
        subca_list = []
        for i in xrange(1, 20):
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
        test_0007_subca_del_replica_subca
        IDM-IPA-TC: ipa ca delete multiple Sub CAs from replica
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
        test_0008_subca_del_multiple_subca_replica
        IDM-IPA-TC: ipa ca delete multiple Sub CAs from Replica
        """
        multihost.replica.kinit_as_admin()
        subca_prefix = "test_0008_subca_"
        subca_list = []
        for i in xrange(1, 20):
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
        test_0009_subca_del_non_existing_subca_replica
        IDM-IPA-TC: ipa ca delete with non-existent Sub CA from replica
        """
        multihost.replica.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0009_subca1"
        # Delete non-existing Sub CA from replica
        cmd = ca_del(multihost.master, subca)
        assert "{0}: Certificate Authority " \
               "not found".format(subca['name']) in cmd[2]

    def test_0010_subca_del_default_subca_replica(self, multihost):
        """
        test_0010_subca_del_default_subca_replica
        IDM-IPA-TC: ipa ca delete with default Sub CA from IPA replica
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
