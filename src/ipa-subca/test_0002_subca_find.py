"""
Testsuite for IPA Lightweight Sub CA - ca-find
"""
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.ca_utils import *
from lib import *
import time
import pytest


class TestSubCAFind(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nUsing following hosts for IPA Lightweight Sub-CA testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("*" * 80)

    def test_0001_subca_help(self, multihost):
        """
        test_0001_subca_help
        IDM-IPA-TC: Check help message for ipa ca
        """
        multihost.master.kinit_as_admin()
        cmd = "ipa help ca"
        print("Running : {0}".format(cmd))
        cmdout = multihost.master.run_command(cmd, raiseonerr=False)
        assert "ca-add" in cmdout.stdout_text
        assert "ca-del" in cmdout.stdout_text
        assert "ca-find" in cmdout.stdout_text
        assert "ca-mod" in cmdout.stdout_text
        assert "ca-show" in cmdout.stdout_text

    def test_0002_subca_find_help(self, multihost):
        """
        test_0002_subca_find_help
        IDM-IPA-TC: Check help message for ipa ca-find
        """
        multihost.master.kinit_as_admin()
        cmd = "ipa help ca-find"
        print("Running : {0}".format(cmd))
        cmdout = multihost.master.run_command(cmd, raiseonerr=False)
        assert "Search for CAs" in cmdout.stdout_text
        assert "Usage: ipa [global-options] ca-find [CRITERIA] [options]" in \
            cmdout.stdout_text

    def test_0003_subca_find_no_param(self, multihost):
        """
        test_0003_subca_find_no_param
        IDM-IPA-TC: ipa ca find without any parameters
        """
        multihost.master.kinit_as_admin()
        subca = {}
        subca['name'] = ''
        cmd = ca_find(multihost.master, subca)
        assert "Name: ipa" in cmd[1]

    def test_0004_subca_find_name_param(self, multihost):
        """
        test_0004_subca_find_name_param
        IDM-IPA-TC: ipa ca find with name option
        """
        multihost.master.kinit_as_admin()
        subca = {}
        subca['name'] = "ipa"
        cmd = ca_find(multihost.master, subca)
        assert "Name: ipa" in cmd[1]

    def test_0005_subca_find_non_existent_subca(self, multihost):
        """
        test_0005_subca_find_non_existent_subca
        IDM-IPA-TC: ipa ca find with non-existent sub ca name option
        """
        multihost.master.kinit_as_admin()
        subca = {}
        subca['name'] = "non_existent_ipa"
        cmd = ca_find(multihost.master, subca)
        assert "0 CAs matched" in cmd[1]
        assert "Number of entries returned 0" in cmd[1]

    def test_0006_subca_find_existent_subca(self, multihost):
        """
        test_0006_subca_find_existent_subca
        IDM-IPA-TC: ipa ca find with existent Sub CA
        """
        multihost.master.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0006_subca1"
        subca['realm'] = multihost.realm
        # Add new Sub CA
        cmd = ca_add(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_add_output(subca, cmd[1])
        # Find Sub CA
        cmd = ca_find(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_find_output(subca, cmd[1])
        # Delete Sub CA
        cmd = ca_del(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_del_output(subca, cmd[1])

    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Class teardown for Sub CA")
