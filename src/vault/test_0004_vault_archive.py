"""
Vault Archive tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements

from .lib import setup_test_prereqs, teardown_test_prereqs
from . import data  # pylint: disable=relative-import


PRIV_VAULT_W_PASSWORD = []


class TestVaultArchive(object):
    """
    Password Vault Archive Tests
    """
    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'archive')
        setup_test_prereqs(multihost, prefix=data.PREFIX)

        global PRIV_VAULT_W_PASSWORD
        PRIV_VAULT_W_PASSWORD = [data.PREFIX + '_vault_priv_w_password']
        multihost.master.qerun(['ipa', 'vault-add'] + PRIV_VAULT_W_PASSWORD +
                               ['--password-file', data.PASS_FILE])

    def class_teardown(self, multihost):
        """ Class Teardown """
        multihost.master.qerun(['ipa', 'vault-del'] + PRIV_VAULT_W_PASSWORD)
        teardown_test_prereqs(multihost, prefix=data.PREFIX)

    def test_0001_successfully_archive_secret_in_vault_from_base64_data_blob(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully archive secret in vault from base64 data blob

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-archive'] + data.PRIV_VAULT + ['--data', data.SECRET_BLOB]
        multihost.master.qerun(runcmd)

    def test_0002_successfully_archive_secret_in_vault_from_input_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully archive secret in vault from input file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-archive'] + data.PRIV_VAULT + ['--in', data.SECRET_FILE]
        multihost.master.qerun(runcmd)

    def test_0003_successfully_archive_secret_in_shared_vault_from_input_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully archive secret in shared vault from input file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-archive'] + data.SHARED_VAULT + ['--in', data.SECRET_FILE]
        multihost.master.qerun(runcmd)

    def test_0004_successfully_archive_secret_in_user_vault_from_input_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully archive secret in user vault from input file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-archive'] + data.USER_VAULT + ['--in', data.SECRET_FILE]
        multihost.master.qerun(runcmd)

    def test_0005_successfully_archive_secret_in_service_vault_from_input_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully archive secret in service vault from input file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-archive'] + data.SERVICE_VAULT + ['--in', data.SECRET_FILE]
        multihost.master.qerun(runcmd)

    def test_0006_successfully_archive_secret_in_vault_from_input_file_with_password_from_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully archive secret in vault from input file with password from file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-archive'] + PRIV_VAULT_W_PASSWORD + \
                 ['--password-file', data.PASS_FILE, '--in', data.SECRET_FILE]
        multihost.master.qerun(runcmd)

    def test_0007_fail_to_archive_secret_in_vault_from_invalid_base64_data_blob(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to archive secret in vault from invalid base64 data blob

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-archive'] + data.PRIV_VAULT + ['--data', data.SECRET_BLOB[:-1]]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="Base64 decoding failed")

    def test_0008_fail_to_archive_secret_in_vault_from_non_existent_input_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to archive secret in vault from non_existent input file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-archive'] + data.PRIV_VAULT + ['--in', data.DNE_FILE]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="No such file")

    def test_0009_fail_to_archive_secret_in_non_existent_vault_from_input_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to archive secret in non_existent vault from input file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-archive'] + data.DNE_VAULT + ['--in', data.SECRET_FILE]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0010_fail_to_archive_secret_in_shared_vault_with_user_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to archive secret in shared vault with user option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-archive', data.PREFIX + '_vault_shared', '--user', data.USER1,
                  '--in', data.SECRET_FILE]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0011_fail_to_archive_secret_in_service_vault_with_user_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to archive secret in service vault with user option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-archive', data.PREFIX + '_vault_service', '--user', data.USER1,
                  '--in', data.SECRET_FILE]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0012_fail_to_archive_secret_in_user_vault_with_non_existent_user(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to archive secret in user vault with non_existent user

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-archive', data.PREFIX + '_vault_user', '--user', 'dneuser',
                  '--in', data.SECRET_FILE]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0013_fail_to_archive_secret_in_user_vault_with_wrong_user(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to archive secret in user vault with wrong user

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-archive', data.PREFIX + '_vault_user', '--user', data.PREFIX + '_user2',
                  '--in', data.SECRET_FILE]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0014_fail_to_archive_secret_in_service_vault_with_non_existent_user(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to archive secret in service vault with non_existent user

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-archive', data.PREFIX + '_vault_service', '--user', 'dneuser',
                  '--in', data.SECRET_FILE]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0015_fail_to_archive_secret_in_service_vault_with_wrong_user(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to archive secret in service vault with wrong user

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-archive', data.PREFIX + '_vault_service', '--user', data.PREFIX + '_user2',
                  '--in', data.SECRET_FILE]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0016_fail_to_archive_large_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to archive large file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-archive', data.PREFIX + '_vault_priv', '--in', data.LARGE_FILE]
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="Size of data exceeds the limit.")
