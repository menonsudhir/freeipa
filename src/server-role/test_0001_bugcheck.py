"""
Overview:
SetUp Requirements:
IPA Server configured on RHEL7.2
"""

import pytest
from ipa_pytests.qe_class import multihost


class Testserverdel(object):

    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_ipaserverdel(self, multihost):
        """
        IDM-IPA-TC: ipa server-del: ipa server-del gives
                    error when run without Server name value
                    bz1369414
        """
        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa', 'server-del'],
                                           stdin_text='\r',
                                           raiseonerr=False)
        print(cmd.stdout_text)
        exp_output = "ipa: ERROR: 'cn' is required"
        if exp_output in cmd.stderr_text:
            print("Server name needs to be specified")
        else:
            pytest.xfail("FAIL")
