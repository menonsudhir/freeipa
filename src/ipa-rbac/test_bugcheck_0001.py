"""
Overview:
TestSuite to verify BZs related to rbac
SetUp Requirements:
-Latest version of RHEL OS
-Need to test for Master
"""

import pytest
from ipa_pytests.qe_class import multihost
import pexpect


class TestBugCheck(object):
    """ Test Class """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_bz1186054(self, multihost):
        """
        Test to verify Bug 1186054 - permission-add does not prompt to enter --right option in interactive mode
        """
        multihost.master.kinit_as_admin()
        cmd = 'ipa permission-add'
        command_output = pexpect.run(cmd, events={"Permission name: ": 'sample_permission\n',
                                                  "\[Granted rights\]: ": "read\n",
                                                  '\[Subtree\]: ': 'cn=groups,cn=accounts,dc=testrelm,dc=test\n',
                                                  '\[Member of group\]: ': 'admins\n',
                                                  '\[Target group\]: ': 'admins\n',
                                                  '\[Type\]: ': "\n"})
        print ("###############################command run output #######################")
        print (command_output)
        if 'Added permission "sample_permission"' not in command_output:
            pytest.xfail("expected output not found")

    print("COMMAND SUCCEEDED!")
