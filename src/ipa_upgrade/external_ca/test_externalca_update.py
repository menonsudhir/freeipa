"""
This is a quick test for External CA upgrade
"""
import time
import pytest
from ipa_pytests.shared.rpm_utils import list_rpms
from ipa_pytests.qe_install import disable_firewall, set_hostname, set_etc_hosts, set_rngd, print_time
from ipa_pytests.shared import paths
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.utils import ipa_version_gte
from ipa_pytests.shared.qe_certutils import certutil
from ipa_pytests.shared.openssl_utils import openssl_util
from ipa_pytests.shared.rpm_utils import get_rpm_version
from ipa_pytests.ipa_upgrade.utils import is_allowed_to_update, upgrade
from ipa_pytests.ipa_upgrade.constants import repo_urls
from ipa_pytests.test_webui import ui_lib
import os
from ipa_pytests.shared.yum_utils import add_repo
from ipa_pytests.shared.user_utils import add_ipa_user, show_ipa_user


class TestExternalCA(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        multihost.realm = multihost.master.domain.realm

        print("Using following hosts for External CA Upgrade testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("*" * 80)

    def test_external_ca_server_install(self, multihost):
        """

        :Title: IDM-IPA-TC: Install IPA with external-ca option and Upgrade

        :Description: Installation of IPA Master using external-ca option after installation perform pre-upgrade setup
                      Then perform upgrade by setting value to upgrade_to and
                      after successful upgrade perform post upgrade tests.

        :Steps:
            1. Set upgrade_from depending on rpm version refer src/ipa_upgrade/constants.py
            2. Install IPA Master with option --external-ca
            3. After installation perform pre-upgrade setup
            4. Perform upgrade
            5. Post upgrade test cases

        :Expectedresults:
            1. Successful IPA Master installation with external-ca option
            2. Successful web ui login
            3. Successful rpm version test after upgrade
            4. Successful log test
            5. After upgrade ipactl should be in running state
            6. users should be exist after upgrade
            7. After upgrade user should be able to login using web-UI

        :Automation: Yes

        :CaseComponent: ipa

        """
        master = multihost.master
        upgrade_from = multihost.config.upgrade_from
        # upgrade_from this can be used to set repo depending on version of packages from where the upgrade is starting.
        # for this refer ipa_upgrade/constants.py

        master = multihost.master
        seconds = 6

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
        cmd = ['dnf', '-y', 'module', 'install', 'idm:4']
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
        print("Current IPA version")
        ipa_version = get_rpm_version(multihost.master, rpm)
        print(ipa_version)
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

        ipa_version = get_rpm_version(multihost.master, 'ipa-server')
        print(ipa_version)

        print ("\n IPA Server Before Updation")
        # checking for ipactl command output before updation
        multihost.master.kinit_as_admin()
        check5 = multihost.master.run_command('ipactl status | grep RUNNING')
        if check5.returncode != 0:
            print("IPA server service not RUNNING.Kindly debug")
        else:
            print("IPA service is running, continuing")
            # creation of users before updation
        user1 = 'testuser1'
        userpass = 'TestP@ss123'
        add_ipa_user(multihost.master, user1, userpass)
        cmd = show_ipa_user(multihost.master, user1)
        assert cmd.returncode == 0

    #def test_web_ui_0001(self, multihost):                            # Commenting UI tests for adding upgrade in CI
    #    """
    #    test for web ui testing before upgrade
    #    """
    #    user1 = 'testuser1'
    #    userpass = 'TestP@ss123'
    #    tp = ui_lib.ui_driver(multihost.master)
    #    try:
    #        tp.setup()
    #        multihost.driver = tp
    #    except StandardError as errval:
    #        pytest.skip("setup_session_skip : %s" % (errval.args[0]))
    #    multihost.driver.init_app(username=user1, password=userpass)
    #    multihost.driver.teardown()

    def test_0001_rpm_version(self, multihost):
        """
        :Title: IDM-IPA-TC: Perform Upgrade and compare rpm version

        """
        rpm = "ipa-server"
        print("Current IPA version")
        ipa_version = get_rpm_version(multihost.master, rpm)

        print(ipa_version)

        # get current ipa version
        # upgrade_from = os.getenv('UPGRADE_FROM', multihost.master.config.upgrade_from)

        # Hard coded path is used for upgrade
        upgrade_to = '7.6.a'
        # print("Upgrading from : %s" % upgrade_from)
        print("Upgrading to : %s" % upgrade_to)

        # upgrade_from is version from which version upgrade is start
        # upgrade_to is version which can be used to set repo as per appropriate version for upgrading the packages
        # for this refer ipa_upgrade/constants.py

        # if is_allowed_to_update(upgrade_to, upgrade_from):
        for repo in repo_urls[upgrade_to]:
            print("Upgrading using repo : %s" % repo)
            add_repo(multihost.master, repo)
        # else:
        #    pytest.xfail("Please specify correct upgrade path")

        cmd = upgrade(multihost.master)  # upgrade starts at this point
        if cmd.returncode == 0:
            updated_version = get_rpm_version(multihost.master, rpm)  # get updated ipa version
            print("Upgraded version is %s " % updated_version)  # prints upgraded version
            if updated_version != ipa_version:
                print("Upgrade rpm test verified")
                print("Upgraded Successfully")
            else:
                pytest.xfail("rpm version check failed  on %s " % multihost.master.hostname)
        else:
            pytest.xfail("Upgrade Failed")

    def test_0002_logs(self, multihost):
        """
        :Title: IDM-IPA-TC:  Test for logs verification
        """
        str1 = 'The ipa-server-upgrade command was successful'
        log2 = multihost.master.run_command(['tail', paths.IPAUPGRADELOGFILE], raiseonerr=True)
        print(log2.stdout_text)
        if str1 in log2.stdout_text:
            print("Log test verified, continuing to next test")
        else:
            pytest.xfail("Log test failed")

    def test_0003_services(self, multihost):
        """
        :Title: IDM-IPA-TC: Test for service verification after upgrade
        """
        # check ipactl status after upgrade

        multihost.master.kinit_as_admin()
        check5 = multihost.master.run_command('ipactl status | grep RUNNING')
        if check5.returncode != 0:
            print("IPA server service not RUNNING.Kindly debug")
        else:
            print("IPA service is running, continuing")

        restart = multihost.master.run_command('ipactl restart', raiseonerr=False)
        print(restart.stdout_text)

        status1 = multihost.master.run_command('ipactl status | grep RUNNING')
        if status1.returncode != 0:
            print("IPA server service not RUNNING.Kindly debug")
        else:
            print("IPA service is running, continuing")

    def test_0004_users(self, multihost):
        """
       :Title: IDM-IPA-TC: Test for user verification after upgrade
        """
        user1 = 'testuser1'
        multihost.master.kinit_as_admin()
        cmd2 = show_ipa_user(multihost.master, user1)
        assert cmd2.returncode == 0
        assert user1 in cmd2.stdout_text
        print("User Successfully verified")

    #def test_webui_0006(self, multihost):                              Commenting UI tests for adding upgrade in CI

    #    """
    #    test for web ui testing after upgrade
    #    """
    #    user1 = 'testuser1'
    #    userpass = 'TestP@ss123'
    #    tp = ui_lib.ui_driver(multihost.master)
    #    try:
    #        tp.setup()
    #        multihost.driver = tp
    #    except StandardError as errval:
    #        pytest.skip("setup_session_skip : %s" % (errval.args[0]))
    #    multihost.driver.init_app(username=user1, password=userpass)
    #    multihost.driver.teardown()

    def class_teardown(self, multihost):
        """Full suite teardown """
        pass
