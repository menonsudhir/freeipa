"""
Vault Modify tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements

from . import data  # pylint: disable=relative-import
import base64
import pytest


class TestVaultModify(object):
    """
    Password Vault Modify Tests
    """
    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'mod')
        multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_priv', '--desc=desc'])

        multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_user', '--desc=desc',
                                '--user=' + data.USER1])

        multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_shared', '--desc=desc',
                                '--shared'])

        multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_service', '--desc=desc',
                                '--service=' + data.SERVICE1])

        multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_priv_std_to_sym'])
        multihost.master.qerun(['ipa', 'vault-archive', data.PREFIX + '_vault_priv_std_to_sym',
                                '--data=' + data.SECRET_BLOB])

        multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_priv_std_to_asym'])
        multihost.master.qerun(['ipa', 'vault-archive', data.PREFIX + '_vault_priv_std_to_asym',
                                '--data=' + data.SECRET_BLOB])

        multihost.master.qerun(['ipa', 'vault-add', '--type=symmetric', data.PREFIX + '_vault_priv_sym_to_asym',
                                '--password=' + data.PASSWORD])
        multihost.master.qerun(['ipa', 'vault-archive', data.PREFIX + '_vault_priv_sym_to_asym',
                                '--password=' + data.PASSWORD, '--data=' + data.SECRET_BLOB])

        multihost.master.qerun(['ipa', 'vault-add', '--type=symmetric', data.PREFIX + '_vault_priv_sym_to_std',
                                '--password=' + data.PASSWORD])
        multihost.master.qerun(['ipa', 'vault-archive', data.PREFIX + '_vault_priv_sym_to_std',
                                '--password=' + data.PASSWORD, '--data=' + data.SECRET_BLOB])

        multihost.master.qerun(['ipa', 'vault-add', '--type=asymmetric', data.PREFIX + '_vault_priv_asym_to_std',
                                '--public-key-file=' + data.PUBKEY_FILE])
        multihost.master.qerun(['ipa', 'vault-archive', data.PREFIX + '_vault_priv_asym_to_std',
                                '--data=' + data.SECRET_BLOB])

        multihost.master.qerun(['ipa', 'vault-add', '--type=asymmetric', data.PREFIX + '_vault_priv_asym_to_sym',
                                '--public-key-file=' + data.PUBKEY_FILE])
        multihost.master.qerun(['ipa', 'vault-archive', data.PREFIX + '_vault_priv_asym_to_sym',
                                '--data=' + data.SECRET_BLOB])

        multihost.master.qerun(['ipa', 'vault-add', '--type=symmetric', data.PREFIX + '_vault_priv_symmetric',
                                '--password=' + data.PASSWORD])

        multihost.master.qerun(['ipa', 'vault-add', '--type=asymmetric', data.PREFIX + '_vault_priv_asymmetric',
                                '--public-key-file=' + data.PUBKEY_FILE])

        multihost.master.qerun(['ipa', 'vault-add', '--type=symmetric', data.PREFIX + '_vault_priv_change_pass',
                                '--password=' + data.PASSWORD])
        multihost.master.qerun(['ipa', 'vault-archive', data.PREFIX + '_vault_priv_change_pass',
                                '--password=' + data.PASSWORD, '--data=' + data.SECRET_BLOB])

    def class_teardown(self, multihost):
        """ Class Teardown """
        pass

    def test_0001_successfully_change_vault_description(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully change vault description

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv', '--desc=new_description']
        multihost.master.qerun(runcmd)

    def test_0002_successfully_change_vault_type_from_standard_to_symmetric(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully change vault type from standard to symmetric

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        secret_retrieved = ""
        out_file = '/root/multihost_tests/std_to_sym_mod_test.' + str(pytest.count)
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv_std_to_sym', '--type=symmetric',
                  '--new-password=' + data.PASSWORD]
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-archive', data.PREFIX + '_vault_priv_std_to_sym', '--password=' + data.PASSWORD,
                  '--in=' + data.SECRET_FILE]
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-retrieve', data.PREFIX + '_vault_priv_std_to_sym', '--password=' + data.PASSWORD,
                  '--out=' + out_file]
        multihost.master.qerun(runcmd)
        secret_retrieved = multihost.master.transport.get_file_contents(out_file)
        assert secret_retrieved == data.SECRET_VALUE

    def test_0003_successfully_change_vault_type_from_symmetric_to_asymmetric(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully change vault type from symmetric to asymmetric

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        out_file = '/root/multihost_tests/sym_to_asym_mod_test.' + str(pytest.count)
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv_sym_to_asym', '--type=asymmetric',
                  '--old-password=' + data.PASSWORD, '--public-key-file=' + data.PUBKEY_FILE]
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-archive', data.PREFIX + '_vault_priv_sym_to_asym',
                  '--in=' + data.SECRET_FILE]
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-retrieve', data.PREFIX + '_vault_priv_sym_to_asym',
                  '--private-key-file=' + data.PRVKEY_FILE, '--out=' + out_file]
        multihost.master.qerun(runcmd)
        secret_retrieved = multihost.master.transport.get_file_contents(out_file)
        assert secret_retrieved == data.SECRET_VALUE

    def test_0004_successfully_change_vault_type_from_asymmetric_to_standard(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully change vault type from asymmetric to standard

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        out_file = '/root/multihost_tests/asym_to_std_mod_test.' + str(pytest.count)
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv_asym_to_std',
                  '--private-key-file=' + data.PRVKEY_FILE, '--type=standard']
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-archive', data.PREFIX + '_vault_priv_asym_to_std', '--in=' + data.SECRET_FILE]
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-retrieve', data.PREFIX + '_vault_priv_asym_to_std', '--out=' + out_file]
        multihost.master.qerun(runcmd)
        secret_retrieved = multihost.master.transport.get_file_contents(out_file)
        assert secret_retrieved == data.SECRET_VALUE

    def test_0005_successfully_change_vault_password_salt(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully change vault password salt

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        newsalt = base64.b64encode('TeStNewSalT')
        out_file = '/root/multihost_tests/asym_to_std_mod_test.' + str(pytest.count)
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv_symmetric', '--salt=' + newsalt,
                  '--old-password=' + data.PASSWORD, '--new-password=' + data.PASSWORD]
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-archive', data.PREFIX + '_vault_priv_symmetric', '--password=' + data.PASSWORD,
                  '--in=' + data.SECRET_FILE]
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-retrieve', data.PREFIX + '_vault_priv_symmetric', '--password=' + data.PASSWORD,
                  '--out=' + out_file]
        multihost.master.qerun(runcmd)
        secret_retrieved = multihost.master.transport.get_file_contents(out_file)
        assert secret_retrieved == data.SECRET_VALUE

    def test_0006_successfully_change_asymmetric_keys_with_blobs(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully change asymmetric keys with blobs

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        old_prvkey = multihost.master.transport.get_file_contents(data.PRVKEY_FILE)
        old_prvkey_blob = base64.b64encode(old_prvkey)
        new_pubkey = multihost.master.transport.get_file_contents(data.NEW_PUBKEY_FILE)
        new_pubkey_blob = base64.b64encode(new_pubkey)
        new_prvkey = multihost.master.transport.get_file_contents(data.NEW_PRVKEY_FILE)
        new_prvkey_blob = base64.b64encode(new_prvkey)
        out_file = '/root/multihost_tests/asym_key_change_mod_test.' + str(pytest.count)
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv_asymmetric',
                  '--private-key="%s"' % old_prvkey_blob, '--public-key="%s"' % new_pubkey_blob]
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-archive', data.PREFIX + '_vault_priv_asymmetric', '--in=' + data.SECRET_FILE]
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-retrieve', data.PREFIX + '_vault_priv_asymmetric',
                  '--private-key="%s"' % new_prvkey_blob, '--out=' + out_file]
        multihost.master.qerun(runcmd)
        secret_retrieved = multihost.master.transport.get_file_contents(out_file)
        assert secret_retrieved == data.SECRET_VALUE

    def test_0007_successfully_change_user_vault_description(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully change user vault description

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_user', '--user=' + data.USER1, '--desc=new_description']
        multihost.master.qerun(runcmd)

    def test_0008_successfully_change_shared_vault_description(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully change shared vault description

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_shared', '--shared', '--desc=new_description']
        multihost.master.qerun(runcmd)

    def test_0009_successfully_change_service_vault_description(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully change service vault description

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_service',
                  '--service=' + data.SERVICE1, '--desc=new_description']
        multihost.master.qerun(runcmd)

    def test_0010_fail_to_change_vault_description_to_same_description(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to change vault description to same description

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv', '--desc=new_description']
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output='no modifications to be performed')

    def test_0011_fail_to_change_non_existent_vault_description(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to change non_existent vault description

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-mod', 'dne_vault', '--desc=new_description']
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output='vault not found')

    def test_0012_fail_to_change_non_existent_vault_type_to_asymmetric(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to change non_existent vault type to asymmetric

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-mod', 'dne_vault', '--type=asymmetric',
                  '--public-key-file=' + data.PUBKEY_FILE]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output='vault not found')

    def test_0013_fail_to_change_non_existent_vault_password_salt(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to change non_existent vault password salt

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        newsalt = base64.b64encode('TeStNewSalT')
        runcmd = ['ipa', 'vault-mod', 'dne_vault', '--salt=' + newsalt,
                  '--old-password=' + data.PASSWORD, '--new-password=' + data.PASSWORD]
        multihost.master.qerun(runcmd, exp_returncode=2, exp_output='vault not found')

    def test_0014_fail_to_change_vault_type_from_standard_to_standard(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to change vault type from standard to standard

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv', '--type=standard']
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output='no modifications to be performed')

    def test_0015_fail_to_change_vault_type_from_symmetric_to_symmetric(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to change vault type from symmetric to symmetric

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # This relies on salt test above
        newsalt = base64.b64encode('TeStNewSalT')
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv_symmetric', '--type=symmetric',
                  '--salt=' + newsalt, '--old-password=' + data.PASSWORD,
                  '--new-password=' + data.PASSWORD]
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output='no modifications to be performed')

    def test_0016_fail_to_change_vault_type_from_asymmetric_to_asymmetric(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to change vault type from asymmetric to asymmetric

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv_asymmetric', '--type=asymmetric'
                  '--private-key-file=' + data.NEW_PRVKEY_FILE,
                  '--public-key-file=' + data.NEW_PUBKEY_FILE]
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output='Missing vault private key')

    def test_0017_fail_to_change_vault_type_to_invalid_type(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to change vault type to invalid type

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv', '--type=invalid']
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output='invalid.*type')

    def test_0018_fail_to_change_vault_password_salt_to_invalid_value(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to change vault password salt to invalid value

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        newsalt = base64.b64encode('TeStNewSalT')
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv_symmetric', '--salt=' + newsalt[:-1],
                  '--old-password=' + data.PASSWORD, '--new-password=' + data.PASSWORD]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output='Base64 decoding failed')

    def test_0019_fail_to_change_vault_public_key_to_invalid_value(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to change vault public key to invalid value

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        valid_key = multihost.master.get_file_contents(data.PUBKEY_FILE)
        invalid_key = base64.b64encode(valid_key)[:-1]
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv_asymmetric', '--public-key="%s"' % invalid_key,
                  '--private-key-file=' + data.NEW_PRVKEY_FILE]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output='Base64 decoding failed')

    def test_0020_successfully_change_symmetric_password_interactively(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: successfully change symmetric password interactively

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        expect = 'set timeout 15\n'
        expect += 'set send_slow {1 .1}\n'
        expect += 'set force_conservative 0\n'
        expect += 'spawn ipa vault-mod  mod_vault_priv_change_pass --change-password\n'
        expect += 'expect "Password: "\n'
        expect += 'send -- "%s\\r"\n' % data.PASSWORD
        expect += 'expect "*assword: " \n'
        expect += 'send -- "1234\\r"\n'
        expect += 'expect "*assword: "\n'
        expect += 'send -- "1234\\r"\n'
        expect += 'expect eof\n'
        exp_file = '/root/multihost_tests/vault_pw_change.exp'
        multihost.master.transport.put_file_contents(exp_file, expect)
        multihost.master.qerun(['expect', '-f', exp_file])

    def test_0021_successfully_change_symmetric_password(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: successfully change symmetric password

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv_symmetric',
                  '--old-password=' + data.PASSWORD, '--new-password=Abcd1234']
        multihost.master.qerun(runcmd)

    def test_0022_fail_to_retrieve_vault_after_password_change(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: fail to retrieve vault after password change

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve', data.PREFIX + '_vault_priv_symmetric', '--password=' + data.PASSWORD]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="Invalid credentials")

    def test_0023_fail_to_retrieve_asymmetric_vault_with_previous_symmetric_password(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: fail to retrieve asymmetric vault with previous symmetric password

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        # mod_vault_priv_sym_to_asym
        runcmd = ['ipa', 'vault-retrieve', data.PREFIX + '_vault_priv_sym_to_asym',
                  '--password=' + data.PASSWORD]
        multihost.master.qerun(runcmd, exp_returncode=1,
                               exp_output="Missing vault private key")

    def test_0024_successfully_change_asymmetric_keys_with_files(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: successfully change asymmetric keys with files

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv_sym_to_asym',
                  '--private-key-file=' + data.PRVKEY_FILE,
                  '--public-key-file=' + data.NEW_PUBKEY_FILE]
        multihost.master.qerun(runcmd)

    def test_0025_fail_to_retrieve_vault_after_changing_keys_with_files(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: fail to retrieve vault after changing keys with files

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-retrieve', data.PREFIX + '_vault_priv_sym_to_asym',
                  '--private-key-file=' + data.PRVKEY_FILE]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="Invalid credentials")

    def test_0026_successfully_change_asymmetric_to_symmetric(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: successfully change asymmetric to symmetric

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv_asym_to_sym', '--type=symmetric',
                  '--private-key-file=' + data.PRVKEY_FILE, '--new-password=' + data.PASSWORD]
        multihost.master.qerun(runcmd)

    def test_0027_fail_to_retrieve_symmetric_vault_with_previous_assymmetric_keys(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: fail to retrieve symmetric vault with previous assymmetric keys

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        cmdstr = ["ipa", "vault-retrieve", "mod_vault_priv_asym_to_sym", "--private-key-file=%s" % data.PRVKEY_FILE]
        cmd = multihost.master.run_command(cmdstr, stdin_text="\n", raiseonerr=False)
        assert cmd.returncode == 1
        assert "Invalid credentials" in cmd.stderr_text

    def test_0028_successfully_change_symmetric_password_with_files(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: successfully change symmetric password with files

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        oldpass_file = "/root/multihost_tests/myoldpass.txt"
        newpass_file = "/root/multihost_tests/mynewpass.txt"
        multihost.master.put_file_contents(oldpass_file, "1234")
        multihost.master.put_file_contents(newpass_file, "12345")
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv_change_pass',
                  '--old-password-file=' + oldpass_file, '--new-password-file=' + newpass_file]
        multihost.master.qerun(runcmd)

    def test_0029_fail_to_retrieve_vault_after_password_change_with_files(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: fail to retrieve vault after password change with files

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        oldpass_file = "/root/multihost_tests/myoldpass.txt"
        runcmd = ['ipa', 'vault-retrieve', data.PREFIX + '_vault_priv_change_pass',
                  '--password-file=' + oldpass_file]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="Invalid credentials")

    def test_0030_successfully_change_symmetric_to_standard(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: successfully change symmetric to standard

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv_sym_to_std', '--type=standard',
                  '--old-password=' + data.PASSWORD]
        multihost.master.qerun(runcmd)

    def test_0031_successfully_change_standard_to_asymmetric(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: successfully change standard to asymmetric

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-mod', data.PREFIX + '_vault_priv_std_to_asym', '--type=asymmetric',
                  '--public-key-file=' + data.PUBKEY_FILE]
        multihost.master.qerun(runcmd)

    def test_0032_fail_to_retrieve_vault_after_changing_keys_with_blobs(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: fail to retrieve vault after changing keys with blobs

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        out_file = '/root/multihost_tests/asym_key_change_mod_test.' + str(pytest.count)
        old_prvkey = multihost.master.transport.get_file_contents(data.PRVKEY_FILE)
        old_prvkey_blob = base64.b64encode(old_prvkey)
        runcmd = ['ipa', 'vault-retrieve', data.PREFIX + '_vault_priv_asymmetric',
                  '--private-key=' + old_prvkey_blob, '--out=' + out_file]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="Invalid credentials")
