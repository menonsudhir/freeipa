"""
Vault Retrieve tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements

from .lib import setup_test_prereqs, teardown_test_prereqs
from . import data  # pylint: disable=relative-import
import base64
import pytest

PRIV_VAULT_W_PASSWORD = []
PRIV_VAULT_W_KEY = []


class TestVaultRetrieve(object):
    """
    Password Vault Retrieve Tests
    """
    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'retrieve')
        setup_test_prereqs(multihost, prefix=data.PREFIX)

        global PRIV_VAULT_W_PASSWORD
        global PRIV_VAULT_W_KEY

        PRIV_VAULT_W_PASSWORD = [data.PREFIX + '_vault_priv_w_password']
        PRIV_VAULT_W_KEY = [data.PREFIX + '_priv_w_key']

        for vault in [data.PRIV_VAULT, data.USER_VAULT, data.SHARED_VAULT, data.SERVICE_VAULT]:
            runcmd = ['ipa', 'vault-archive'] + vault + ['--data=' + data.SECRET_BLOB]
            multihost.master.qerun(runcmd)

        runcmd = ['ipa', 'vault-add'] + PRIV_VAULT_W_PASSWORD + \
                 ['--type=symmetric', '--password=' + data.PASSWORD]
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-archive'] + PRIV_VAULT_W_PASSWORD + \
                 ['--data=' + data.SECRET_BLOB, '--password=' + data.PASSWORD]
        multihost.master.qerun(runcmd)

        # create private vault with keys and archive secret there
        runcmd = ['ipa', 'vault-add'] + PRIV_VAULT_W_KEY + \
                 ['--type=asymmetric', '--public-key-file=' + data.PUBKEY_FILE]
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-archive'] + PRIV_VAULT_W_KEY + ['--data=' + data.SECRET_BLOB]
        multihost.master.qerun(runcmd)

    def class_teardown(self, multihost):
        """ Class Teardown """
        teardown_test_prereqs(multihost, prefix="retrieve")

    def test_0001_successfully_retrieve_secret_from_vault_without_lock(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully retrieve secret from vault without lock

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve'] + data.PRIV_VAULT
        multihost.master.qerun(runcmd, exp_output=data.SECRET_BLOB)

    def test_0002_successfully_retrieve_secret_from_user_vault_without_lock(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully retrieve secret from user vault without lock

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve'] + data.USER_VAULT
        multihost.master.qerun(runcmd, exp_output=data.SECRET_BLOB)

    def test_0003_successfully_retrieve_secret_from_shared_vault_without_lock(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully retrieve secret from shared vault without lock

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve'] + data.SHARED_VAULT
        multihost.master.qerun(runcmd, exp_output=data.SECRET_BLOB)

    def test_0004_successfully_retrieve_secret_from_service_vault_without_lock(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully retrieve secret from service vault without lock

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve'] + data.SERVICE_VAULT
        multihost.master.qerun(runcmd, exp_output=data.SECRET_BLOB)

    def test_0005_successfully_retrieve_secret_from_vault_with_password(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully retrieve secret from vault with password

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve'] + PRIV_VAULT_W_PASSWORD + ['--password=' + data.PASSWORD]
        multihost.master.qerun(runcmd, exp_output=data.SECRET_BLOB)

    def test_0006_successfully_retrieve_secret_from_vault_with_password_from_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully retrieve secret from vault with password from file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve'] + PRIV_VAULT_W_PASSWORD + \
                 ['--password-file=' + data.PASS_FILE]
        multihost.master.qerun(runcmd, exp_output=data.SECRET_BLOB)

    def test_0007_successfully_retrieve_secret_from_vault_with_public_key(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully retrieve secret from vault with public key

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        prvkey = multihost.master.transport.get_file_contents(data.PRVKEY_FILE)
        prvkey_blob = base64.b64encode(prvkey)
        runcmd = ['ipa', 'vault-retrieve'] + PRIV_VAULT_W_KEY + ['--private-key=%s' % prvkey_blob]
        multihost.master.qerun(runcmd, exp_output=data.SECRET_BLOB)

    def test_0008_successfully_retrieve_secret_from_vault_with_public_key_from_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully retrieve secret from vault with public key from file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve'] + PRIV_VAULT_W_KEY + \
                 ['--private-key-file=' + data.PRVKEY_FILE]
        multihost.master.qerun(runcmd, exp_output=data.SECRET_BLOB)

    def test_0009_fail_to_retrieve_secret_from_non_existent_vault_without_lock(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to retrieve secret from non_existent vault without lock

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve'] + data.DNE_VAULT
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0010_fail_to_retrieve_secret_from_user_vault_without_lock_with_service_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to retrieve secret from user vault without lock with service option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve', data.PREFIX + '_vault_user',
                  '--service=' + data.SERVICE1]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0011_fail_to_retrieve_secret_from_shared_vault_without_lock_with_user_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to retrieve secret from shared vault without lock with user option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve', data.PREFIX + '_vault_shared',
                  '--user=' + data.USER1]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0012_fail_to_retrieve_secret_from_service_vault_without_lock_with_shared_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to retrieve secret from service vault without lock with shared option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve', data.PREFIX + '_vault_service', '--shared']
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0013_fail_to_retrieve_secret_from_user_vault_without_lock_with_non_existent_user(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to retrieve secret from user vault without lock with non_existent user

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve', data.PREFIX + '_vault_user', '--user=DNE']
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0014_fail_to_retrieve_secret_from_service_vault_without_lock_with_non_existent_service(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to retrieve secret from service vault without lock with non_existent service

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve', data.PREFIX + '_vault_service',
                  '--service=DNE' + '/' + multihost.master.hostname]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output="vault not found")

    def test_0015_fail_to_retrieve_secret_from_vault_with_invalid_password(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to retrieve secret from vault with invalid password

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve'] + PRIV_VAULT_W_PASSWORD + ['--password=invalid']
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="Invalid credentials")

    def test_0016_fail_to_retrieve_secret_from_vault_with_non_existent_password_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to retrieve secret from vault with non_existent password file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve'] + PRIV_VAULT_W_PASSWORD + \
                 ['--password-file=' + data.DNE_FILE]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="No such file or directory")

    def test_0017_fail_to_retrieve_secret_from_vault_with_invalid_public_key_value(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to retrieve secret from vault with invalid public key value

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        new_prvkey = multihost.master.transport.get_file_contents(data.NEW_PRVKEY_FILE)
        new_prvkey_blob = base64.b64encode(new_prvkey)
        runcmd = ['ipa', 'vault-retrieve'] + PRIV_VAULT_W_KEY + ['--private-key=%s' % new_prvkey_blob]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="Invalid credentials")

    def test_0018_fail_to_retrieve_secret_from_vault_with_non_existent_public_key_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to retrieve secret from vault with non_existent public key file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve'] + PRIV_VAULT_W_KEY + \
                 ['--private-key-file=' + data.DNE_FILE]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="No such file or directory")

    def test_0019_successfully_retrieve_vault_on_replica_without_kra(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully retrieve vault on replica without KRA

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        multihost.replica.kinit_as_admin()
        runcmd = ['ipa', 'vault-retrieve'] + data.PRIV_VAULT
        multihost.replica.qerun(runcmd, exp_output=data.SECRET_BLOB)
