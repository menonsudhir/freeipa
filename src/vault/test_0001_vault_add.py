"""
Vault Add tests
"""

# pylint: disable=too-many-public-methods,no-self-use

import pytest
import base64
import data  # pylint: disable=relative-import
from .lib import delete_all_vaults


class TestVaultAdd(object):
    """
    Password Vault Add Tests
    """

    def class_setup(self, multihost):
        """ Class Setup """
        pass

    def class_teardown(self, multihost):
        """ Class Teardown """
        delete_all_vaults(multihost.master)

    def test_0001_successfully_add_standard_private_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add standard private vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--type=standard', vault_name]
        multihost.master.qerun(runcmd)

    def test_0002_successfully_add_symmetric_private_vault_password(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add symmetric private vault password

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--type=symmetric', '--password=1234', vault_name]
        multihost.master.qerun(runcmd)

    def test_0003_successfully_add_symmetric_private_vault_password_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add symmetric private vault password_file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--type=symmetric',
                  '--password-file=%s' % data.PASS_FILE, vault_name]
        multihost.master.qerun(runcmd)

    def test_0004_successfully_add_asymmetric_private_vault_public_key(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add asymmetric private vault public_key

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        pubkey = multihost.master.transport.get_file_contents(data.PUBKEY_FILE)
        pubkey = base64.b64encode(pubkey)
        runcmd = ['ipa', 'vault-add', '--type=asymmetric',
                  '--public-key=%s' % pubkey, vault_name]
        multihost.master.qerun(runcmd)

    def test_0005_successfully_add_asymmetric_private_vault_public_key_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add asymmetric private vault public_key_file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--type=asymmetric',
                  '--public-key-file=%s' % data.PUBKEY_FILE, vault_name]
        multihost.master.qerun(runcmd)

    def test_0006_successfully_add_standard_user_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add standard user vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--user=%s' % data.USER1, '--type=standard',
                  vault_name]
        multihost.master.qerun(runcmd)

    def test_0007_successfully_add_symmetric_user_vault_password(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add symmetric user vault password

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--user=%s' % data.USER1, '--type=symmetric',
                  '--password=1234', vault_name]
        multihost.master.qerun(runcmd)

    def test_0008_successfully_add_symmetric_user_vault_password_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add symmetric user vault password_file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--user=%s' % data.USER1, '--type=symmetric',
                  '--password-file=%s' % data.PASS_FILE, vault_name]
        multihost.master.qerun(runcmd)

    def test_0009_successfully_add_asymmetric_user_vault_public_key(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add asymmetric user vault public_key

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        pubkey = multihost.master.transport.get_file_contents(data.PUBKEY_FILE)
        pubkey = base64.b64encode(pubkey)
        runcmd = ['ipa', 'vault-add', '--user=%s' % data.USER1, '--type=asymmetric',
                  '--public-key=%s' % pubkey, vault_name]
        multihost.master.qerun(runcmd)

    def test_0010_successfully_add_asymmetric_user_vault_public_key_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add asymmetric user vault public_key_file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--user=%s' % data.USER1, '--type=asymmetric',
                  '--public-key-file=%s' % data.PUBKEY_FILE, vault_name]
        multihost.master.qerun(runcmd)

    def test_0011_successfully_add_standard_shared_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add standard shared vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--shared', '--type=standard', vault_name]
        multihost.master.qerun(runcmd)

    def test_0012_successfully_add_symmetric_shared_vault_password(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add symmetric shared vault password

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--shared', '--type=symmetric',
                  '--password=1234', vault_name]
        multihost.master.qerun(runcmd)

    def test_0013_successfully_add_symmetric_shared_vault_password_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add symmetric shared vault password_file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--shared', '--type=symmetric',
                  '--password-file=%s' % data.PASS_FILE, vault_name]
        multihost.master.qerun(runcmd)

    def test_0014_successfully_add_asymmetric_shared_vault_public_key(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add asymmetric shared vault public_key

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        pubkey = multihost.master.transport.get_file_contents(data.PUBKEY_FILE)
        pubkey = base64.b64encode(pubkey)
        runcmd = ['ipa', 'vault-add', '--shared', '--type=asymmetric',
                  '--public-key=%s' % pubkey, vault_name]
        multihost.master.qerun(runcmd)

    def test_0015_successfully_add_asymmetric_shared_vault_public_key_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add asymmetric shared vault public_key_file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--shared', '--type=asymmetric',
                  '--public-key-file=%s' % data.PUBKEY_FILE, vault_name]
        multihost.master.qerun(runcmd)

    def test_0016_successfully_add_standard_service_vault(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add standard service vault

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--service=%s' % data.SERVICE1, '--type=standard',
                  vault_name]
        multihost.master.qerun(runcmd)

    def test_0017_successfully_add_symmetric_service_vault_password(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add symmetric service vault password

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--service=%s' % data.SERVICE1, '--type=symmetric',
                  '--password=1234', vault_name]
        multihost.master.qerun(runcmd)

    def test_0018_successfully_add_symmetric_service_vault_password_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add symmetric service vault password_file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--service=%s' % data.SERVICE1, '--type=symmetric',
                  '--password-file=%s' % data.PASS_FILE, vault_name]
        multihost.master.qerun(runcmd)

    def test_0019_successfully_add_asymmetric_service_vault_public_key(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add asymmetric service vault public_key

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        pubkey = multihost.master.transport.get_file_contents(data.PUBKEY_FILE)
        pubkey = base64.b64encode(pubkey)
        runcmd = ['ipa', 'vault-add', '--service=%s' % data.SERVICE1, '--type=asymmetric',
                  '--public-key=%s' % pubkey, vault_name]
        multihost.master.qerun(runcmd)

    def test_0020_successfully_add_asymmetric_service_vault_public_key_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully add asymmetric service vault public_key_file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--service=%s' % data.SERVICE1, '--type=asymmetric',
                  '--public-key-file=%s' % data.PUBKEY_FILE, vault_name]
        multihost.master.qerun(runcmd)

    def test_0021_fail_to_add_vault_with_same_name(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add vault with same name

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--password=1234', vault_name]
        multihost.master.qerun(runcmd)
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="already exists")

    def test_0022_fail_to_add_vault_with_invalid_type(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add vault with invalid type

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--type=DNE', vault_name]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="invalid.*type")

    def test_0023_fail_to_add_vault_with_non_existent_password_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add vault with non_existent password file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--password-file=%s' % data.DNE_FILE, vault_name]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="invalid.*password-file")

    def test_0024_fail_to_add_vault_with_invalid_public_key_blob(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add vault with invalid public key blob

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--type=asymmetric', '--public-key="%s"' % data.INVALID_KEY, vault_name]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="invalid.*ipavaultpublickey")

    def test_0025_fail_to_add_vault_with_non_existent_public_key_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add vault with non_existent public key file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--type=asymmetric', '--public-key-file=%s' % data.DNE_FILE, vault_name]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="invalid.*public-key-file")

    def test_0026_fail_to_add_vault_with_invalid_public_key_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add vault with invalid public key file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--type=asymmetric', '--public-key-file=/etc/hosts', vault_name]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="invalid.*ipavaultpublickey")

    def test_0027_fail_to_add_vault_as_both_shared_and_user(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add vault as both shared and user

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--user=%s' % data.USER1, '--shared',
                  '--password=123', vault_name]
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="options cannot be specified simultaneously")

    def test_0028_fail_to_add_vault_as_both_user_and_service(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add vault as both user and service

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--user=%s' % data.USER1, '--service=%s' % data.SERVICE1,
                  '--password=123', vault_name]
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="options cannot be specified simultaneously")

    def test_0029_fail_to_add_vault_as_both_service_and_shared(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add vault as both service and shared

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--service=%s' % data.SERVICE1, '--shared',
                  '--password=123', vault_name]
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="options cannot be specified simultaneously")

    def test_0030_fail_to_add_asymmetric_vault_without_public_key_or_pk_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add asymmetric vault without public _key or pk file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--type=asymmetric', vault_name]
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="Missing vault public key")

    def test_0031_fail_to_add_asymmetric_vault_with_password_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add asymmetric vault with password_file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--type=asymmetric',
                  '--password-file=%s' % data.PASS_FILE, vault_name]
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="Password can be specified only for symmetric vault")

    def test_0032_fail_to_add_asymmetric_vault_with_password(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add asymmetric vault with password

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--type=asymmetric', '--password=1234', vault_name]
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="Password can be specified only for symmetric vault")

    def test_0033_fail_to_add_symmetric_vault_with_public_key_file(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add symmetric vault with public_key_file

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        runcmd = ['ipa', 'vault-add', '--type=symmetric',
                  '--public-key-file=%s' % data.PUBKEY_FILE, vault_name]
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="Public key can be specified only for asymmetric vault")

    def test_0034_fail_to_add_symmetric_vault_with_public_key(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to add symmetric vault with public_key

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        vault_name = "idmqe_vault_%s" % pytest.count  # pylint: disable=no-member
        pubkey = multihost.master.transport.get_file_contents(data.PUBKEY_FILE)
        pubkey = base64.b64encode(pubkey)
        runcmd = ['ipa', 'vault-add', '--type=symmetric',
                  '--public-key="%s"' % pubkey, vault_name]
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="Public key can be specified only for asymmetric vault")
