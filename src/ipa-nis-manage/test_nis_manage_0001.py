"""
Overview:
SetUp Requirements:
IPA Server configured on RHEL7.2
"""

import pytest
from ipa_pytests.qe_class import multihost


class Testnismanage(object):

    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")

    def test_0001_bz1329275(self, multihost):
        """
        IDM-IPA-TC: ipa-nis-manage: ipa-nis-manage command has status option
                    bz1329275
        """
        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa-nis-manage', '--help'],
                                           raiseonerr=False)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        if 'status' in cmd.stdout_text:
            print("status option is available")
        else:
            pytest.xfail("bz1329275 exists")

    def test_002_pluginstatus(self, multihost):
        """
        IDM-IPA-TC: ipa-nis-manage: check status of nis manage plugin
        """
        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa-nis-manage', 'status'],
                                           stdin_text=multihost.master.config.admin_pw,
                                           raiseonerr=False)
        if cmd.stdout_text == 'Plugin is enabled':
            print("plugin is already enabled")
        elif cmd.stdout_text == 'Plugin is not enabled':
            print("plugin is not enabled")

    def test_002_enableplugin(self, multihost):
        """
        IDM-IPA-TC: ipa-nis-manage: enable nis manage plugin
        """
        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa-nis-manage', 'enable'],
                                           stdin_text=multihost.master.config.admin_pw,
                                           raiseonerr=False)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        exp_output = "Enabling plugin"
        if exp_output in cmd.stdout_text:
            print("nis manage plugin is enabled")
        else:
            pytest.xfail("FAIL")

    def test_003_disableplugin(self, multihost):
        """
        IDM-IPA-TC: ipa-nis-manage: disable nis plugin and check status
        """
        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa-nis-manage', 'disable'],
                                           stdin_text=multihost.master.config.admin_pw,
                                           raiseonerr=False)
        print(cmd.stdout_text)
        exp_output = "This setting will not take effect"
        if exp_output in cmd.stdout_text:
            print("nis manage plugin is disabled")
        elif cmd.stdout_text == "Enabling plugin":
            print("Plugin is enabled")
        else:
            pytest.xfail("FAIL")
