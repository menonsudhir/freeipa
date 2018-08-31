"""
Vault Miscellaneous Functional tests
"""

# pylint: disable=too-many-public-methods,no-self-use,global-statement,too-many-statements


from .lib import setup_test_prereqs, teardown_test_prereqs
from . import data  # pylint: disable=relative-import


class TestVaultMiscFunc(object):
    """
    Password Vault Misc Functional Tests
    """

    def class_setup(self, multihost):
        """ Class Setup """
        data.init(multihost, 'misc')
        setup_test_prereqs(multihost, prefix=data.PREFIX)

        short_service_vault = [data.PREFIX + '_vault_short_service', '--service=' + data.PREFIX + '_service1/' +
                               multihost.master.hostname + '@' + multihost.master.domain.realm]
        long_service_vault = [data.PREFIX + '_vault_long_service', '--service=' + data.PREFIX + '_service1/' +
                              multihost.master.hostname + '@' + multihost.master.domain.realm]

        runcmd = ['ipa', 'vault-add', '--type=standard'] + short_service_vault
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-add', '--type=standard'] + long_service_vault
        multihost.master.qerun(runcmd)

    def class_teardown(self, multihost):
        """ Class Teardown """
        teardown_test_prereqs(multihost, prefix=data.PREFIX)

    def test_0001_successfully_manage_service_vaults_with_normalized_service_name(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault:  Successfully manage service vaults with normalized service name

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """
        service_short = data.PREFIX + '_service1/' + multihost.master.hostname
        service_long = service_short + '@' + multihost.master.domain.realm

        multihost.master.kinit_as_admin()

        # check ldap for short service container dne
        cn = 'cn=' + service_short + ',cn=services,cn=vaults,cn=kra,' + \
             multihost.master.domain.basedn.replace('"', '')
        runcmd = ['ldapsearch', '-Y', 'GSSAPI', '-b', cn]
        multihost.master.qerun(runcmd, exp_returncode=32)

        # check ldap for long service container exists
        cn = 'cn=' + service_long + ',cn=services,cn=vaults,cn=kra,' + \
             multihost.master.domain.basedn.replace('"', '')
        runcmd = ['ldapsearch', '-Y', 'GSSAPI', '-b', cn]
        multihost.master.qerun(runcmd, exp_returncode=0)

        # check vault container shows long service name when looking up short service
        runcmd = ['ipa', 'vaultcontainer-show', '--service=' + service_short]
        multihost.master.qerun(runcmd, exp_output="Vault service: " + service_long)

        # check vault container shows long service name when looking up long service
        runcmd = ['ipa', 'vaultcontainer-show', '--service=' + service_long]
        multihost.master.qerun(runcmd, exp_output="Vault service: " + service_long)

        # check vault find shows both vaults when looking up short service
        runcmd = ['ipa', 'vault-find', '--service=' + service_short]
        cmd = multihost.master.run_command(runcmd)
        assert cmd.stdout_text.find(data.PREFIX + '_vault_short_service') > 0
        assert cmd.stdout_text.find(data.PREFIX + '_vault_long_service') > 0

        # check vault find shows both vaults when looking up long service
        runcmd = ['ipa', 'vault-find', '--service=' + service_long]
        cmd = multihost.master.run_command(runcmd)
        assert cmd.stdout_text.find(data.PREFIX + '_vault_short_service') > 0
        assert cmd.stdout_text.find(data.PREFIX + '_vault_long_service') > 0

        # make sure no containers for either long or short service exist after del
        runcmd = ['ipa', 'vault-del', data.PREFIX + '_vault_short_service', '--service=' + service_short]
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-del', data.PREFIX + '_vault_long_service', '--service=' + service_long]
        multihost.master.qerun(runcmd)
        runcmd = ['ipa', 'vault-find', '--service=' + service_short]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="entries returned 0")
        runcmd = ['ipa', 'vault-find', '--service=' + service_long]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="entries returned 0")

    def test_0002_successfully_manage_service_vault_with_service(self, multihost):
        """
        :Title: IDM-IPA-TC: Vault: Successfully manage service vault with service

        :Requirement: IDM-IPA: Password Vault - Key and Secret Storage

        :Casecomponent: ipa

        :Caseautomation: automated

        """

        service_base = data.PREFIX + '_service_management'
        svault1 = service_base + '1'
        svault2 = service_base + '2'
        service1 = svault1 + '/' + multihost.master.hostname
        service2 = svault2 + '/' + multihost.master.hostname

        for svc in ['1', '2']:
            svc_name = service_base + svc
            svc_file = '/root/multihost_tests/' + svc_name
            # create CSR and private key
            runcmd = ['openssl', 'req', '-new', '-newkey', 'rsa:2048', '-days', '365', '-nodes',
                      '-keyout', svc_file + '.prvkey', '-out', svc_file + '.csr',
                      '-subj', '/CN=' + multihost.master.hostname]
            multihost.master.qerun(runcmd)
            # get public key from private key
            runcmd = ['openssl', 'pkey', '-pubout', '-in', svc_file + '.prvkey', '-out',
                      svc_file + '.pubkey']
            multihost.master.qerun(runcmd)
            # create service and sign cert using CSR
            runcmd = ['ipa', 'cert-request', svc_file + '.csr', '--add', '--principal',
                      svc_name + '/' + multihost.master.hostname]
            multihost.master.qerun(runcmd)
            # output cert for service
            runcmd = ['ipa', 'service-show', svc_name + '/' + multihost.master.hostname, '--out',
                      svc_file + '.pem']
            multihost.master.qerun(runcmd)
            # get keytab file for service
            runcmd = ['ipa-getkeytab', '-s', multihost.master.hostname,
                      '-p', svc_name + '/' + multihost.master.hostname,
                      '-k', svc_file + '.keytab']
            multihost.master.qerun(runcmd)

        runcmd = ['kinit', service1, '-k', '-t',
                  '/root/multihost_tests/' + svault1 + '.keytab']
        multihost.master.qerun(runcmd)

        runcmd = ['ipa', 'vault-add', svault1, '--service', service1, '--type', 'asymmetric',
                  '--public-key-file', '/root/multihost_tests/' + svault1 + '.pubkey']
        multihost.master.qerun(runcmd)

        runcmd = ['ipa', 'vault-archive', svault1, '--service', service1,
                  '--in', data.SECRET_FILE]
        multihost.master.qerun(runcmd)

        outfile = '/root/multihost_tests/' + svault1 + ".secret.out"
        runcmd = ['ipa', 'vault-retrieve', svault1, '--service', service1,
                  '--private-key-file', '/root/multihost_tests/' + svault1 + '.prvkey',
                  '--out', outfile]
        multihost.master.qerun(runcmd)
        runcmd = ['cat', outfile]
        multihost.master.qerun(runcmd, exp_output=data.SECRET_VALUE)

        # should fail because Vault administrators are only ones allowed to add owners
        runcmd = ['ipa', 'vaultcontainer-add-owner', '--service=' + service1,
                  '--services=' + service2]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="Insufficient access")

        multihost.master.kinit_as_admin()

        runcmd = ['ipa', 'vaultcontainer-add-owner', '--service=' + service1,
                  '--services=' + service2]
        multihost.master.qerun(runcmd)

        runcmd = ['kinit', service1, '-k', '-t',
                  '/root/multihost_tests/' + svault1 + '.keytab']
        multihost.master.qerun(runcmd)

        runcmd = ['ipa', 'vault-add-owner', svault1, '--service=' + service1,
                  '--services=' + service2]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="Insufficient access")

        multihost.master.kinit_as_admin()

        runcmd = ['ipa', 'vault-add-owner', svault1, '--service=' + service1,
                  '--services=' + service2]
        multihost.master.qerun(runcmd)

        runcmd = ['ipa', 'vault-add-member', svault1, '--service=' + service1,
                  '--services=' + service2]
        multihost.master.qerun(runcmd)

        runcmd = ['kinit', service2, '-k', '-t',
                  '/root/multihost_tests/' + svault2 + '.keytab']
        multihost.master.qerun(runcmd)

        runcmd = ['ipa', 'vault-remove-member', svault1, '--service=' + service1,
                  '--services=' + service2]
        multihost.master.qerun(runcmd)

        runcmd = ['kinit', service1, '-k', '-t',
                  '/root/multihost_tests/' + svault1 + '.keytab']
        multihost.master.qerun(runcmd)

        runcmd = ['ipa', 'vault-remove-owner', svault1, '--service=' + service1,
                  '--services=' + service2]
        multihost.master.qerun(runcmd, exp_returncode=1, exp_output="Insufficient access")

        multihost.master.kinit_as_admin()

        runcmd = ['ipa', 'vault-remove-owner', svault1, '--service=' + service1,
                  '--services=' + service2]
        multihost.master.qerun(runcmd)

        runcmd = ['ipa', 'service-del', service1]
        multihost.master.qerun(runcmd)

        runcmd = ['ipa', 'service-del', service2]
        multihost.master.qerun(runcmd)

        service_base = data.PREFIX + '_service_management'
        for i in ['1', '2']:
            for suffix in ['csr', 'prvkey', 'pubkey', 'pem', 'keytab', 'secret.out']:
                svc_file = '/root/multihost_tests/' + service_base + i + '.' + suffix
                if multihost.master.transport.file_exists(svc_file):
                    multihost.master.transport.remove_file(svc_file)
