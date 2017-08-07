"""
Vault Config-Show tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements


class TestVaultConfigShow(object):
    """
    Password Vault Config Show Tests
    """

    def test_0001_successfully_show_vaultconfig(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully show vaultconfig

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vaultconfig-show']
        multihost.master.qerun(runcmd, exp_output="Transport Certificate: ")

    def test_0002_successfully_show_vaultconfig_and_output_to_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully show vaultconfig and output to file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        outfile = '/tmp/ipa_vaultconfig_show.out'
        runcmd = ['ipa', 'vaultconfig-show', '--transport-out=' + outfile]
        multihost.master.qerun(runcmd, exp_output="Transport Certificate:")

        runcmd = ['openssl', 'x509', '-inform', 'der', '-in', outfile, '-noout', '-subject']
        multihost.master.qerun(runcmd, exp_output="KRA Transport Certificate")
