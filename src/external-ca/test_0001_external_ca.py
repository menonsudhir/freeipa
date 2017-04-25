"""
This is a quick test for External CA
"""
import time
import tempfile
import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.qe_certutils import certutil
from ipa_pytests.shared.openssl_utils import openssl_util
import ipa_pytests.shared.paths as paths


class TestExternalCA(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        multihost.realm = multihost.master.domain.realm

        print("Using following hosts for External CA testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("*" * 80)

    def test_0001_external_ca_server_install(self, multihost):
        """ test_0001_external_ca_server_install
        IDM-IPA-TC: Install IPA Server using external-ca option """
        master = multihost.master
        seconds = 1
        cmd = [paths.IPASERVERINSTALL,
               '-p', master.config.admin_pw,
               '-a', master.config.admin_pw,
               '-r', master.domain.realm,
               '--setup-dns',
               '--forwarder', master.config.dns_forwarder,
               '--domain', master.domain.name,
               '--realm', master.domain.realm,
               '--external-ca', '-U']
        print("\nRunning : [%s]" % " ".join(cmd))
        cmd = master.run_command(cmd, raiseonerr=False)
        if cmd.returncode != 0:
            pytest.xfail("Unable to install ipa-server using --external-ca")
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
        certs.selfsign_cert(ca_subject, ca_nick, options=['-m', '1', '--extSKID'])

        print("\nSleeping for [%d] seconds" % seconds)
        time.sleep(seconds)
        install_cert_file = '/root/ipa.csr'
        cert_der_file = "%s/req.csr" % (nssdb_dir)
        cmd = ['req', '-outform', 'der', '-in', install_cert_file,
               '-out', cert_der_file]
        openssl_util(master, cmd)

        out_der_file = "%s/external.crt" % (nssdb_dir)
        certs.sign_csr(cert_der_file, out_der_file, ca_nick, options=['--extSKID'])
        # Generate PEM file
        out_pem_file = "%s/external.pem" % (nssdb_dir)
        cmdstr = ['x509', '-inform', 'der', '-in', out_der_file,
                  '-out', out_pem_file]
        openssl_util(master, cmdstr)

        ca_cert_file = "%s/ca.crt" % (nssdb_dir)
        certs.export_cert(ca_nick, ca_cert_file)
        # Create Certificate chain
        chain_cert_file = "%s/chain.crt" % (nssdb_dir)
        pem_file_content = master.get_file_contents(out_pem_file)
        ca_cert_file_content = master.get_file_contents(ca_cert_file)
        master.put_file_contents(chain_cert_file,
                                 pem_file_content + ca_cert_file_content)

        cmd = [paths.IPASERVERINSTALL, '--external-cert-file',
               chain_cert_file, '-p', master.config.admin_pw, '-U',
               '-p', master.config.admin_pw,
               '-a', master.config.admin_pw,
               '-r', master.domain.realm]
        print("Running : {0}".format(" ".join(cmd)))
        cmd = master.run_command(cmd, raiseonerr=False)
        if cmd.returncode != 0:
            pytest.fail("Failed to install IPA Server using "
                        "--external-cert-file")
        print("Successfully installed IPA Server using --external-ca")

    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Class teardown for external CA")
