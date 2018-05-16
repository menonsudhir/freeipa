"""
Overview:
SetUp Requirements For IPA server upgrade
"""
import pytest
import time
from ipa_pytests.shared.rpm_utils import get_rpm_version
from ipa_pytests.shared import paths
from selenium import webdriver
from ipa_pytests.qe_class import multihost
import os
from ipa_pytests.ipa_upgrade.constants import repo_urls
from ipa_pytests.shared.qe_certutils import certutil
from ipa_pytests.shared.yum_utils import add_repo
from ipa_pytests.ipa_upgrade.utils import upgrade, is_allowed_to_update
from ipa_pytests.shared.openssl_utils import openssl_util
from ipa_pytests.qe_install import setup_master
from ipa_pytests.shared.user_utils import add_ipa_user, show_ipa_user
from ipa_pytests.shared.ipa_cert_utils import ipa_ca_cert_update
from ipa_pytests.test_webui import ui_lib
from ipa_pytests.shared.utils import ipa_version_gte
from distutils.version import LooseVersion


class Testmaster(object):
    """ Test Class """

    def class_setup(self, multihost):
        """ Setup for class """
        multihost.realm = multihost.master.domain.realm

        print("Using following hosts for CA Cert Renewal testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("*" * 80)
        upgrade_from = multihost.config.upgrade_from
        # upgrade_from this can be used to set repo depending on version of packages from where the upgrade is starting.
        # for this refer ipa_upgrade/constants.py

    def test_0001_cert_renewal(self, multihost):
        """

        :Title: IDM-IPA-TC: Convert Self-signed CA to External CA signed server

        :Description: Check installation of IPA Master from self-signed to external CA signed server

        :Setup:

            1. RHEL 7.4 system

        :Steps:
            1. Set upgrade_from depending on rpm version refer src/ipa_upgrade/constants.py
            2. Install IPA Master which will install self-signed CA
            3. Check if IPA Master is installed successfully
            4. Check if ipactl works with various operations
            5. Use ipa-cacert-update with --external-ca and sign given CSR with External CA
            6. Renew CA certificate using ipa-certupdate
            7. perform pre-upgrade setup
            8. Perform upgrade
            9. Post upgrade test cases
            10.Again convert external CA to self-signed CA


        :Expectedresults:
            1. No errors or warnings during installation procedure
            2. Successful IPA Master installation
            3. Successful ipactl operations
            4. Successful ipa-cacert-update command
            5. Conversion using ipa-cacert-update should be successful
            6. Conversion using ipa-cacert-update should be successful from external CA to self signed
            7. After upgrade ipactl should be in running state
            8. users should be exist after upgrade
            9.After upgrade user should be able to login using web-UI

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

        print "Current IPA version"
        rpm = "ipa-server"
        ipa_version = get_rpm_version(multihost.master, rpm)
        print ipa_version
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

        # List all Cert before renew
        master.kinit_as_admin()
        print "List all Certs before renew"
        stdout, stderr = certs.list_certs(db_dir='/etc/pki/pki-tomcat/alias')
        print stdout

        cmd = [paths.IPACACERTMANAGE, 'renew', '--external-cert-file=%s' % chain_cert_file]
        print("Running : {0}".format(" ".join(cmd)))
        cmd = master.run_command(cmd, raiseonerr=False)
        if cmd.returncode != 0:
            pytest.fail("Failed to update External CA Cert")

        master.kinit_as_admin()

        cmd = ipa_ca_cert_update(master)
        assert cmd.returncode == 0

        print "List all Certs after cert-update"
        stdout1, stderr1 = certs.list_certs(db_dir='/etc/pki/pki-tomcat/alias')
        print stdout1

        print ("\n IPA Server Before upgrade")
        # checking for ipactl command output before upgrade
        multihost.master.kinit_as_admin()
        check5 = multihost.master.run_command('ipactl status | grep RUNNING')
        if check5.returncode != 0:
            print("IPA server service not RUNNING.Kindly debug")
        else:
            print("IPA service is running, continuing")

        # creation of users before upgrade
        user1 = 'testuser1'
        userpass = 'TestP@ss123'
        add_ipa_user(multihost.master, user1, userpass)
        cmd = show_ipa_user(multihost.master, user1)
        assert cmd.returncode == 0

        ipa_version = get_rpm_version(multihost.master, 'ipa-server')
        print ipa_version

    def test_web_ui_0001(self, multihost):
        """
        test for web ui testing before upgrade
        """
        user1 = 'testuser1'
        userpass = 'TestP@ss123'
        tp = ui_lib.ui_driver(multihost.master)
        try:
            tp.setup()
            multihost.driver = tp
        except StandardError as errval:
            pytest.skip("setup_session_skip : %s" % (errval.args[0]))
        multihost.driver.init_app(username=user1, password=userpass)
        multihost.driver.teardown()

    def test_upgrade_0002(self, multihost):
        """
        test for automation of upgradation of packeges
        test for rpm comparison
        """
        rpm = "ipa-server"
        print "Current IPA version"
        ipa_version = get_rpm_version(multihost.master, rpm)                      # get current ipa version

        print ipa_version

        upgrade_from = os.getenv('UPGRADE_FROM', multihost.master.config.upgrade_from)
        upgrade_to = os.getenv('UPGRADE_TO', multihost.master.config.upgrade_to)
        print("Upgrading from : %s" % upgrade_from)
        print("Upgrading to : %s" % upgrade_to)

        # upgrade_from is version from which version upgrade is start
        # upgrade_to is version which can be used to set repo as per appropriate version for upgrading the packages
        # for this refer ipa_upgrade/constants.py

        if is_allowed_to_update(upgrade_to, upgrade_from):
            for repo in repo_urls[upgrade_to]:
                print("Upgrading using repo : %s" % repo)
                cmdupdate = add_repo(multihost.master, repo)
        else:
            pytest.xfail("Please specify correct upgrade path")

        # certificates before upgrade
        nssdb_dir = '/tmp/nssdb'
        certs = certutil(multihost.master, nssdb_dir)
        stdout1, stderr1 = certs.list_certs(db_dir='/etc/pki/pki-tomcat/alias')

        print "certificates before upgrade"
        print stdout1
        print stderr1

        cmd = upgrade(multihost.master)                                                   # upgrade starts at this point
        if cmd.returncode == 0:
            updated_version = get_rpm_version(multihost.master, rpm)  # get updated ipa version
            print "Upgraded version is %s " % updated_version  # prints upgraded version
            if LooseVersion(updated_version) > LooseVersion(ipa_version):
                print "Upgrade rpm test verified"
                print("Upgraded Successfully")
            else:
                pytest.xfail("rpm version check failed  on %s " % multihost.master.hostname)
        else:
            pytest.xfail("Upgrade Failed")

        # certificates after upgrade
        certs2 = certutil(multihost.master, nssdb_dir)
        stdout2, stderr2 = certs2.list_certs(db_dir='/etc/pki/pki-tomcat/alias')

        print "certificates before upgrade"
        print stdout1
        print stderr1
        print "certificates after upgrade"
        print stdout2
        print stderr2

    def test_services_verification_0003(self, multihost):
        """
        test for service verification after upgrade
        """
        # check ipactl status after upgrade

        multihost.master.kinit_as_admin()

        check5 = multihost.master.run_command('ipactl status | grep RUNNING')
        if check5.returncode != 0:
            print("IPA server service not RUNNING.Kindly debug")
        else:
            print("IPA service is running, continuing")

        restart = multihost.master.run_command('ipactl restart', raiseonerr=False)
        print restart.stdout_text

        status1 = multihost.master.run_command('ipactl status | grep RUNNING')
        if status1.returncode != 0:
            print("IPA server service not RUNNING.Kindly debug")
        else:
            print("IPA service is running, continuing")

    def test_logs_0004(self, multihost):
        """
        test for automation of upgradation of packeges
        test for logs verification
        """

        str1 = 'The ipa-server-upgrade command was successful'
        log2 = multihost.master.run_command(['tail', paths.IPAUPGRADELOGFILE], raiseonerr=True)
        print log2.stdout_text
        if str1 in log2.stdout_text:
            print "Log test verified, continuing to next test"
        else:
            pytest.xfail("Log test failed")

    def test_users_0005(self, multihost):
        """
        test for automation of upgradation of packeges
        test for service verification
        """
        user1 = 'testuser1'
        multihost.master.kinit_as_admin()
        cmd2 = show_ipa_user(multihost.master, user1)
        assert cmd2.returncode == 0
        assert user1 in cmd2.stdout_text
        print("User Successfully verified")

    def test_cert_renew_to_self_signed_0006(self, multihost):
        """
        Test for ca-cert renew to self-signed after upgrade
        """
        nssdb_dir = '/tmp/nssdb'
        certs = certutil(multihost.master, nssdb_dir)
        stdout1, stderr1 = certs.list_certs(db_dir='/etc/pki/pki-tomcat/alias')
        print stdout1
        print stderr1

        cmd = [paths.IPACACERTMANAGE, 'renew', '--self-signed']
        print("Running : {0}".format(" ".join(cmd)))
        cmd = multihost.master.run_command(cmd, raiseonerr=False)
        if cmd.returncode != 0:
            pytest.fail("Failed to update using self-signed certificate")

        cmd = ipa_ca_cert_update(multihost.master)
        assert cmd.returncode == 0
        stdout2, stderr2 = certs.list_certs(db_dir='/etc/pki/pki-tomcat/alias')
        print stdout2
        print stderr2

    def test_cert_services_verification_0007(self, multihost):
        """
        Test for services verification ca-cert renew t0 self-signed
        """
        multihost.master.kinit_as_admin()
        status1 = multihost.master.run_command('ipactl status | grep RUNNING')
        if status1.returncode != 0:
            print("IPA server service not RUNNING.Kindly debug")
        else:
            print("IPA service is running, continuing")

        restart = multihost.master.run_command('ipactl restart', raiseonerr=False)
        print restart.stdout_text

        status3 = multihost.master.run_command('ipactl status | grep RUNNING')
        if status3.returncode != 0:
            print("IPA server service not RUNNING.Kindly debug")
        else:
            print("IPA service is running, continuing")

    def test_webui_0008(self, multihost):
        """
        test for web ui testing after upgrade
        """
        user1 = 'testuser1'
        userpass = 'TestP@ss123'
        tp = ui_lib.ui_driver(multihost.master)
        try:
            tp.setup()
            multihost.driver = tp
        except StandardError as errval:
            pytest.skip("setup_session_skip : %s" % (errval.args[0]))
        multihost.driver.init_app(username=user1, password=userpass)
        multihost.driver.teardown()

    def class_teardown(self, multihost):
        """Full suite teardown """
        pass
