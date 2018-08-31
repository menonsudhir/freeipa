"""
This is a quick test for CA Cert Renewal scenarios
"""
import time
import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.qe_certutils import certutil
from ipa_pytests.shared.openssl_utils import openssl_util
import ipa_pytests.shared.paths as paths
from ipa_pytests.qe_install import setup_master
from ipa_pytests.shared.ipa_cert_utils import ipa_ca_cert_update
from ipa_pytests.shared.rpm_utils import get_rpm_version
from ipa_pytests.shared.utils import ipa_version_gte


class TestCaCertRenewal(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        multihost.realm = multihost.master.domain.realm

        print("Using following hosts for CA Cert Renewal testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("*" * 80)

    def test_0001_self_signed_to_external_ca(self, multihost):
        """

        :Title: IDM-IPA-TC: Convert Self-signed CA to External CA signed server

        :Description: Check installation of IPA Master from self-signed to external CA signed server

        :Setup:

            1. RHEL 7.4 system

        :Steps:
            1. Install IPA Master which will install self-signed CA
            2. Check if IPA Master is installed successfully
            3. Check if ipactl works with various operations
            4. Use ipa-cacert-update with --external-ca and sign given CSR with External CA
            5. Renew CA certificate using ipa-certupdate
            6. Again convert external CA to self-signed CA

        :Expectedresults:
            1. No errors or warnings during installation procedure
            2. Successful IPA Master installation
            3. Successful ipactl operations
            4. Successful ipa-cacert-update command
            5. Conversion using ipa-cacert-update should be successful
            6. Conversion using ipa-cacert-update should be successful from external CA to self signed

        :Automation: Yes

        :CaseComponent: ipa

        """
        master = multihost.master
        seconds = 1
        setup_master(master)
        # Create tmp directory
        nssdb_dir = '/tmp/nssdb'
        if master.transport.file_exists(nssdb_dir):
            cmd = master.run_command([paths.RM, '-rf', nssdb_dir],
                                     raiseonerr=False)
            if cmd.returncode != 0:
                pytest.fail("Failed to remove directory %s" % nssdb_dir)

        print("\nCreating nss database at [%s]" % nssdb_dir)
        ca_nick = 'ca'
        ca_subject = "cn=Test_CA"

        certs = certutil(master, nssdb_dir)
        print("\nCreating self-signed CA certificate")

        if ipa_version_gte(multihost.master, '4.5.0'):
            certs.selfsign_cert(ca_subject, ca_nick, options=['-m', '1', '--extSKID'])
        else:
            certs.selfsign_cert(ca_subject, ca_nick, options=['-m', '1'])

        # Create
        master.kinit_as_admin()
        cmd = master.run_command([paths.IPACACERTMANAGE, 'renew', '--external-ca'], raiseonerr=False)
        assert cmd.returncode == 0

        # Sign Certificate using external CA
        print("\nSleeping for [%d] seconds" % seconds)
        time.sleep(seconds)
        install_cert_file = '/var/lib/ipa/ca.csr'
        cert_der_file = "%s/req.csr" % nssdb_dir
        cmd = ['req', '-outform', 'der', '-in', install_cert_file,
               '-out', cert_der_file]
        openssl_util(master, cmd)

        out_der_file = "%s/external.crt" % nssdb_dir
        print("Current IPA version")
        rpm = "ipa-server"
        ipa_version = get_rpm_version(multihost.master, rpm)
        print(ipa_version)
        if ipa_version_gte(multihost.master, '4.5.0'):
            print("Ipa version is %s" % ipa_version, "using extSKID option installing Ipa server ")
            certs.sign_csr(cert_der_file, out_der_file, ca_nick, options=['--extSKID'])
        else:
            print("Ipa version is %s" % ipa_version, "without extSKID option installing Ipa server ")
            certs.sign_csr(cert_der_file, out_der_file, ca_nick)

        # Generate PEM file
        out_pem_file = "%s/external.pem" % nssdb_dir
        cmdstr = ['x509', '-inform', 'der', '-in', out_der_file,
                  '-out', out_pem_file]
        openssl_util(master, cmdstr)

        ca_cert_file = "%s/ca.crt" % nssdb_dir
        certs.export_cert(ca_nick, ca_cert_file)
        # Create Certificate chain
        chain_cert_file = "%s/chain.crt" % nssdb_dir
        pem_file_content = master.get_file_contents(out_pem_file)
        ca_cert_file_content = master.get_file_contents(ca_cert_file)
        master.put_file_contents(chain_cert_file,
                                 pem_file_content + ca_cert_file_content)

        #bz-1506526 automation
        ca_csr_out_file = '/tmp/ca_csr.out'
        cmd = ['req', '-in', install_cert_file, '-noout', '-text', '-out', ca_csr_out_file]
        openssl_util(master, cmd)
        ca_csr_out = master.get_file_contents(ca_csr_out_file)
        cmd = ['openssl', 'x509', '-in', out_pem_file, '-noout', '-text']
        print("Running : %s" % " ".join(cmd))
        cmd1 = master.run_command(cmd, raiseonerr=False)

        cmd = ['openssl', 'x509', '-in', ca_cert_file, '-noout', '-text']
        print("Running : %s" % " ".join(cmd))
        cmd2 = master.run_command(cmd, raiseonerr=False)

        if 'CA:TRUE' in ca_csr_out and 'CA:TRUE' in cmd1.stdout_text and 'CA:TRUE' in cmd2.stdout_text:
            print("Success : bz-1506526 verified")
        else:
            pytest.xfail("Failed : bz-1506526 found..!!")

        # List all Cert before renew
        master.kinit_as_admin()
        certs.list_certs(db_dir='/etc/pki/pki-tomcat/alias')

        cmd = [paths.IPACACERTMANAGE, 'renew', '--external-cert-file=%s' % chain_cert_file]
        print("Running : {0}".format(" ".join(cmd)))
        cmd = master.run_command(cmd, raiseonerr=False)
        if cmd.returncode != 0:
            pytest.fail("Failed to update External CA Cert")

        master.kinit_as_admin()

        cmd = ipa_ca_cert_update(master)
        assert cmd.returncode == 0

        certs.list_certs(db_dir='/etc/pki/pki-tomcat/alias')

        cmd = [paths.IPACACERTMANAGE, 'renew', '--self-signed']
        print("Running : {0}".format(" ".join(cmd)))
        cmd = master.run_command(cmd, raiseonerr=False)
        if cmd.returncode != 0:
            pytest.fail("Failed to update using self-signed certificate")

        master.kinit_as_admin()

        cmd = ipa_ca_cert_update(master)
        assert cmd.returncode == 0

        certs.list_certs(db_dir='/etc/pki/pki-tomcat/alias')

    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Class teardown for CA Cert Renewal")
