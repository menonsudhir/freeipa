"""
This is a quick test for External CA
"""
import time
import tempfile
import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_install import (disable_firewall, set_hostname,
                                   set_etc_hosts, set_rngd, print_time)
from ipa_pytests.shared.rpm_utils import list_rpms, get_rpm_version
from ipa_pytests.shared.user_utils import add_ipa_user, show_ipa_user, del_ipa_user
from ipa_pytests.shared.qe_certutils import certutil
from ipa_pytests.shared.openssl_utils import openssl_util
import ipa_pytests.shared.paths as paths
from ipa_pytests.qe_install import ipa_version_gte

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
        """

        :Title: IDM-IPA-TC: Install IPA Server using external-ca option

        :Description: Check installation of IPA Master using external-ca option

        :Setup:

        1. RHEL 7.4 system

        :Steps:
            1. Install IPA Master with option --external-ca
            2. Check if IPA Master is installed successfully
            3. Check if ipactl works with various operations

        :Expectedresults:
            1. No errors or warnings during installation procedure
            2. Successful IPA Master installation
            3. Successful ipactl operations

        :Automation: No

        :CaseComponent: ipa

        """
        master = multihost.master
        seconds = 1

        print("Listing RPMS")
        list_rpms(master)
        print("Disabling Firewall")
        disable_firewall(master)
        print("Setting hostname")
        set_hostname(master)
        print("Setting /etc/hosts")
        set_etc_hosts(master)
        print("Setting up RNGD")
        set_rngd(master)

        print_time()
        print("Installing required packages")
        cmd = ['dnf', '-y', 'module', 'install', 'idm:4/dns']
        master.qerun(cmd, exp_returncode=0)

        print_time()

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
        if ipa_version_gte(multihost.master, '4.5.0'):
            certs.selfsign_cert(ca_subject, ca_nick, options=['-m', '1', '--extSKID'])
        else:
            certs.selfsign_cert(ca_subject, ca_nick, options=['-m', '1'])

        print("\nSleeping for [%d] seconds" % seconds)
        time.sleep(seconds)
        install_cert_file = '/root/ipa.csr'
        cert_der_file = "%s/req.csr" % (nssdb_dir)
        cmd = ['req', '-outform', 'der', '-in', install_cert_file,
               '-out', cert_der_file]
        openssl_util(master, cmd)
        out_der_file = "%s/external.crt" % (nssdb_dir)
        rpm = "ipa-server"
        print ("Current IPA version")
        ipa_version = get_rpm_version(multihost.master, rpm)
        print (ipa_version)
        if ipa_version_gte(multihost.master, '4.5.0'):
            print("Ipa version is %s" % ipa_version, "using extSKID option installing Ipa server ")
            certs.sign_csr(cert_der_file, out_der_file, ca_nick, options=['--extSKID'])
        else:
            print("Ipa version is %s" % ipa_version, "without extSKID option installing Ipa server ")
            certs.sign_csr(cert_der_file, out_der_file, ca_nick)
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

    def test_0002_external_ca_server_install_log_check(self, multihost):
        """

        :Title: IDM-IPA-TC: Install IPA Server install log check

        :Description: Check if server install logs contians ca subject name
                      and assert for success message in logs

        :Setup:

        1. RHEL 7.4 system

        :Steps:
            1. grep "CA_Subject" /var/log/ipaserver-install.log
            2. tail -1 /var/log/ipaserver-install.log
        :Expectedresults:
            1. CA sunject name should be present in logs
            2. Success message should be present in logs

        :Automation: No

        :CaseComponent: ipa

        """
        master = multihost.master
        cmd_arg = ["tail", "-1", "/var/log/ipaserver-install.log"]
        print("Running : " + str(cmd_arg))
        cmd = master.run_command(cmd_arg, raiseonerr=False)
        if cmd.returncode != 0:
            pytest.fail("Failed : ..!!")
        assert "The ipa-server-install command was successful" in cmd.stdout_text
        print("Success : Successfully installed IPA Server")

        #check if log server-install logs contains external ca_subject
        cmd_arg = ["grep", "Test_CA", "/var/log/ipaserver-install.log"]
        print("Running : " + str(cmd_arg))
        cmd = master.run_command(cmd_arg, raiseonerr=False)
        if cmd.returncode != 0:
            pytest.fail("Failed : external ca subject not found in /var/log/ipaserver-install.log..!!")
        print("Success : external ca subject found in /var/log/ipaserver-install.log..!!")

    def test_0003_external_ca_server_install_ipa_services_check(self, multihost):
        """

        :Title: IDM-IPA-TC: Install IPA Services check after server install

        :Description: Check if ipa services are up and running

        :Setup:

        1. RHEL 7.4 system

        :Steps:
            1. ipactl status
        :Expectedresults:
            1. ipa services should be up and running

        :Automation: No

        :CaseComponent: ipa

        """
        master = multihost.master
        #check if ipa services are running after extrnal-ca install
        cmd_arg = ["ipactl", "status"]
        print("Running : " + str(cmd_arg))
        cmd = master.run_command(cmd_arg, raiseonerr=False)
        if cmd.returncode != 0:
            pytest.fail("Failed : ipa services not running..!!")
        print(cmd.stdout_text)
        print("Success : ipa services are running..!!")

    def test_0004_external_ca_server_install_kinit(self, multihost):
        master = multihost.master
        #check if kinit happens
        passwd = "Secret123"
        user = "admin"
        master.run_command(['kinit', user], stdin_text=passwd, raiseonerr=False)
        cmd = master.run_command('klist')
        if cmd.returncode != 0:
            pytest.fail("Failed : kinit failed..!!")
        print(cmd.stdout_text)
        print("Success : kinit succeed..!!")

    def test_0005_external_ca_server_install_user_check(self, multihost):
        """

        :Title: IDM-IPA-TC: Install IPA Server install user check

        :Description: Check if user can be added, deleted and shown

        :Setup:

        1. RHEL 7.4 system

        :Steps:
            1. ipa user-add
            2. ipa user-show
            3. ipa user-del
        :Expectedresults:
            1. user should be added
            2. user should be listed
            3. user should be deleted

        :Automation: No

        :CaseComponent: ipa

        """
        master = multihost.master
        #add ipa user
        testuser1 = "testuser1"
        cmd = add_ipa_user(master, testuser1)
        if cmd.returncode != 0:
            pytest.fail("Failed : Adding testuser1 failed..!!")
        print(cmd.stdout_text)
        print("Success : tesuser1 added successfully..!!")

        #show ipa user
        cmd = show_ipa_user(master, testuser1)
        if cmd.returncode != 0:
            pytest.fail("Failed : testuser1 not found..!!")
        print(cmd.stdout_text)
        print("Success : tesuser1 found..!!")

        #del ipa user
        cmd = del_ipa_user(master, testuser1)
        if cmd.returncode != 0:
            pytest.fail("Failed : testuser1 deletion failed..!!")
        print(cmd.stdout_text)
        print("Success : tesuser1 deleted..!!")

        #show ipa user
        cmd = show_ipa_user(master, testuser1)
        if cmd.returncode == 0:
            pytest.fail("Failed : testuser1 found after deletion..!!")
        print(cmd.stdout_text)
        print("Success : tesuser1 not found..!!")

    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Class teardown for external CA")
