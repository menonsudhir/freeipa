"""
Vault Find tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements

from . import data  # pylint: disable=relative-import


class TestVaultFind(object):
    """
    Password Vault Find Tests
    """
    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'find')
        # Create 4 vaults each for priv, user, shared, and service
        for num in range(4):
            idx = str(num)
            multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_priv_' + idx])
            multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_user_' + idx,
                                    '--user=' + data.USER1])
            multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_shared_' + idx,
                                    '--shared'])
            multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_service_' + idx,
                                    '--service=' + data.SERVICE1])

        # Create 4 more service vaults for http/master
        for num in range(4, 8):
            idx = str(num)
            multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_service_' + idx,
                                    '--service=http/' + multihost.master.hostname])

        multihost.master.qerun(['ipa', 'vault-add', '--type=standard', data.PREFIX + '_vault_priv_w_desc',
                                '--desc=my_vault_with_description'])
        multihost.master.qerun(['ipa', 'vault-add', '--type=symmetric', data.PREFIX + '_vault_priv_symmetric',
                                '--password=' + data.PASSWORD])
        multihost.master.qerun(['ipa', 'vault-add', '--type=asymmetric', data.PREFIX + '_vault_priv_asymmetric',
                                '--public-key-file=' + data.PUBKEY_FILE])

    def class_teardown(self, multihost):
        """ Class Teardown """
        pass

    def test_0001_successfully_find_all_shared_vaults(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully find all shared vaults

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', '--shared']
        multihost.master.qerun(runcmd)
        cmd = multihost.master.run_command(runcmd)
        assert data.PREFIX + '_vault_shared_0' in cmd.stdout_text
        assert data.PREFIX + '_vault_shared_1' in cmd.stdout_text
        assert data.PREFIX + '_vault_shared_2' in cmd.stdout_text
        assert data.PREFIX + '_vault_shared_3' in cmd.stdout_text
        assert 'entries returned 4' in cmd.stdout_text

    def test_0002_successfully_find_all_user_vaults_for_user(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully find all user vaults for user

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', '--user=' + data.USER1]
        multihost.master.qerun(runcmd)
        cmd = multihost.master.run_command(runcmd)
        assert data.PREFIX + '_vault_user_0' in cmd.stdout_text
        assert data.PREFIX + '_vault_user_1' in cmd.stdout_text
        assert data.PREFIX + '_vault_user_2' in cmd.stdout_text
        assert data.PREFIX + '_vault_user_3' in cmd.stdout_text
        assert 'entries returned 4' in cmd.stdout_text

    def test_0003_successfully_find_all_service_vaults_for_service(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully find all service vaults for service

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', '--service=' + data.SERVICE1]
        multihost.master.qerun(runcmd)
        cmd = multihost.master.run_command(runcmd)
        assert data.PREFIX + '_vault_service_0' in cmd.stdout_text
        assert data.PREFIX + '_vault_service_1' in cmd.stdout_text
        assert data.PREFIX + '_vault_service_2' in cmd.stdout_text
        assert data.PREFIX + '_vault_service_3' in cmd.stdout_text
        assert 'entries returned 4' in cmd.stdout_text

    def test_0004_successfully_find_vault_by_name(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully find vault by name

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', data.PREFIX + '_vault_priv_0']
        cmd = multihost.master.run_command(runcmd)
        assert data.PREFIX + '_vault_priv_0' in cmd.stdout_text
        assert 'entries returned 1' in cmd.stdout_text

    def test_0005_successfully_find_shared_vault_by_name(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully find shared vault by name

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', data.PREFIX + '_vault_shared_0', '--shared']
        cmd = multihost.master.run_command(runcmd)
        assert data.PREFIX + '_vault_shared_0' in cmd.stdout_text
        assert 'entries returned 1' in cmd.stdout_text

    def test_0006_successfully_find_service_vault_by_name(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully find service vault by name

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', data.PREFIX + '_vault_service_0',
                  '--service=' + data.SERVICE1]
        cmd = multihost.master.run_command(runcmd)
        assert data.PREFIX + '_vault_service_0' in cmd.stdout_text
        assert 'entries returned 1' in cmd.stdout_text

    def test_0007_successfully_find_vault_by_name_with_name_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully find vault by name with name option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', '--name=find_vault_priv_0']
        cmd = multihost.master.run_command(runcmd)
        assert data.PREFIX + '_vault_priv_0' in cmd.stdout_text
        assert 'entries returned 1' in cmd.stdout_text

    def test_0008_successfully_find_vault_by_description(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully find vault by description

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', '--desc=my_vault_with_description']
        cmd = multihost.master.run_command(runcmd)
        assert data.PREFIX + '_vault_priv_w_desc' in cmd.stdout_text
        assert 'entries returned 1' in cmd.stdout_text

    def test_0009_successfully_find_vault_by_type_standard(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully find vault by type standard

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', '--desc=my_vault_with_description']
        cmd = multihost.master.run_command(runcmd)
        assert data.PREFIX + '_vault_priv_w_desc' in cmd.stdout_text
        assert 'entries returned 1' in cmd.stdout_text

    def test_0010_successfully_find_vault_by_type_symmetric(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully find vault by type symmetric

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', '--type=symmetric']
        multihost.master.qerun(runcmd)
        cmd = multihost.master.run_command(runcmd)
        assert data.PREFIX + '_vault_priv_symmetric' in cmd.stdout_text
        assert 'entries returned 1' in cmd.stdout_text

    def test_0011_successfully_find_vault_by_type_asymmetric(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully find vault by type asymmetric

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', '--type=asymmetric']
        multihost.master.qerun(runcmd)
        cmd = multihost.master.run_command(runcmd)
        assert data.PREFIX + '_vault_priv_asymmetric' in cmd.stdout_text
        assert 'entries returned 1' in cmd.stdout_text

    def test_0012_successfully_find_vaults_and_only_list_primary_key(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully find vaults and only list primary key

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', '--pkey-only']
        cmd = multihost.master.run_command(runcmd)
        assert data.PREFIX + '_vault_priv_' in cmd.stdout_text
        assert 'Type:' not in cmd.stdout_text

    def test_0013_successfully_find_vaults_with_time_limit(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully find vaults with time limit

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', '--timelimit=1']
        cmd = multihost.master.run_command(runcmd)
        assert data.PREFIX + '_vault_priv_' in cmd.stdout_text

    def test_0014_successfully_find_vaults_with_size_limit(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully find vaults with size limit

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', '--sizelimit=1']
        cmd = multihost.master.run_command(runcmd, raiseonerr=False)
        assert data.PREFIX + '_vault_priv_' in cmd.stdout_text
        assert 'entries returned 1' in cmd.stdout_text

    def test_0015_fail_to_find_non_existent_vault_by_name(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to find non_existent vault by name

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', 'dne']
        cmd = multihost.master.run_command(runcmd, raiseonerr=False)
        assert 'entries returned 0' in cmd.stdout_text
        assert cmd.returncode is 1

    def test_0016_fail_to_find_user_vault_with_service_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to find user vault with service option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', data.PREFIX + '_vault_user_0',
                  '--service=' + data.SERVICE1]
        cmd = multihost.master.run_command(runcmd, raiseonerr=False)
        assert 'entries returned 0' in cmd.stdout_text
        assert cmd.returncode is 1

    def test_0017_fail_to_find_shared_vault_with_user_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to find shared vault with user option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', data.PREFIX + '_vault_shared_0', '--user=' + data.USER1]
        cmd = multihost.master.run_command(runcmd, raiseonerr=False)
        assert 'entries returned 0' in cmd.stdout_text
        assert cmd.returncode is 1

    def test_0018_fail_to_find_service_vault_with_shared_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to find service vault with shared option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', data.PREFIX + '_vault_service_0', '--shared']
        cmd = multihost.master.run_command(runcmd, raiseonerr=False)
        assert 'entries returned 0' in cmd.stdout_text
        assert cmd.returncode is 1

    def test_0019_fail_to_find_type_standard_vault_with_type_asymmetric_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to find type standard vault with type asymmetric option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', data.PREFIX + '_vault_priv_0', '--type=asymmetric']
        cmd = multihost.master.run_command(runcmd, raiseonerr=False)
        assert 'entries returned 0' in cmd.stdout_text
        assert cmd.returncode is 1

    def test_0020_fail_to_find_type_symmetric_vault_with_type_standard_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to find type symmetric vault with type standard option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', data.PREFIX + '_vault_priv_symmetric', '--type=standard']
        cmd = multihost.master.run_command(runcmd, raiseonerr=False)
        assert 'entries returned 0' in cmd.stdout_text
        assert cmd.returncode is 1

    def test_0021_fail_to_find_type_asymmetric_vault_with_type_symmetric_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Fail to find type asymmetric vault with type symmetric option

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', data.PREFIX + '_vault_priv_asymmetric', '--type=symmetric']
        cmd = multihost.master.run_command(runcmd, raiseonerr=False)
        assert 'entries returned 0' in cmd.stdout_text
        assert cmd.returncode is 1

    def test_0022_successfully_find_all_service_vaults(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully find all service vaults

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', '--services']
        cmd = multihost.master.run_command(runcmd)
        assert '_service_' in cmd.stdout_text

    def test_0023_successfully_find_all_user_vaults(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully find all user vaults

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        runcmd = ['ipa', 'vault-find', '--users']
        cmd = multihost.master.run_command(runcmd)
        assert '_user_' in cmd.stdout_text
        assert '_priv_' in cmd.stdout_text
        assert 'entries returned 11' in cmd.stdout_text
