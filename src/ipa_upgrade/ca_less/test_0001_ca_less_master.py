"""
Overview:
SetUp Requirements For IPA server upgrade
"""
import pytest
import time
from ipa_pytests.shared.rpm_utils import get_rpm_version
from ipa_pytests.shared import paths
from distutils.version import LooseVersion
from selenium import webdriver
from ipa_pytests.qe_class import multihost
from ipa_pytests.ipa_upgrade.constants import repo_urls
from ipa_pytests.shared.qe_certutils import certutil
from ipa_pytests.shared.yum_utils import add_repo
from ipa_pytests.ipa_upgrade.utils import upgrade, is_allowed_to_update
from ipa_pytests.shared.utils import run_pk12util
from ipa_pytests.qe_install import setup_master_ca_less
from ipa_pytests.shared.user_utils import add_ipa_user, show_ipa_user
from ipa_pytests.shared.utils import stop_firewalld
from ipa_pytests.test_webui import ui_lib

class Testmaster(object):
    """ Test Class """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)
        master = multihost.master
        passwd = 'Secret123'
        seconds = 10

        upgrade_from = '7.3.b'
        # upgrade_from this can be used to set repo depending on version of packages from where the upgrade is starting.
        # for this refer ipa_upgrade/constants.py

        for repo in repo_urls[upgrade_from]:
            cmd = add_repo(multihost.master, repo)

        """Adding command to stop firewall service on master """
        stop_firewalld(multihost.master)

        # Create tmp directory
        nssdb_dir = '/tmp/nssdb'
        if master.transport.file_exists(nssdb_dir):
            cmd = master.run_command([paths.RM, '-rf', nssdb_dir],
                                      raiseonerr=False)
            if cmd.returncode != 0:
                pytest.fail("Failed to remove directory %s" % nssdb_dir)

        print("\n2. Creating nss database at [%s]" % nssdb_dir)
        ca_nick = 'ca'
        ca_subject = "cn=Test_CA"

        server_nick = 'server'
        server_subject = 'cn=%s' % master.hostname

        certs = certutil(master, nssdb_dir)
        print("\n3. Creating self-signed CA certificate")
        certs.selfsign_cert(ca_subject, ca_nick, options=['-m', '1'])

        print("\nSleeping for [%d] seconds" % seconds)
        time.sleep(seconds)
        print("\n4. Creating self-signed server certificate")
        certs.create_server_cert(server_subject, server_nick, ca_nick)

        # Export certificates
        server_cert_file = '{}/server.p12'.format(nssdb_dir)

        print("\n5. Exporting certificates from database")
        if master.transport.file_exists(server_cert_file):
            master.run_command([paths.RM, '-rf', server_cert_file],raiseonerr=False)

        cmdstr = ['-o', server_cert_file, '-n', 'server', '-d',
                  nssdb_dir, '-k', certs.password_file, '-W', passwd]
        cmd = run_pk12util(master, cmdstr)
        if cmd.returncode != 0:
            pytest.fail("Failed to export certificates from "
                        "nssdb [%s]" % nssdb_dir)
        else:
            print("\nSuccessfully exported certificate from nssdb "
                  "stored at [%s]" % server_cert_file)
        # Install ipa-server using self-signed CA and Server certificates
        cmd = setup_master_ca_less(multihost.master, passwd, passwd, passwd,
                                   server_cert_file, server_cert_file)
        if cmd.returncode != 0:
            print(cmd.stdout_text, cmd.stderr_text)
            pytest.fail("Failed to install IPA server on machine [%s]"
                        % master.hostname)
        else:
            print("\nIPA server installed successfully")

        ipa_version = get_rpm_version(multihost.master, 'ipa-server')
        print ipa_version

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

    def test_web_ui_0001(self, multihost):
        """
        test for web ui testing before upgrade
        """
        user1 = 'testuser1'
        userpass = 'TestP@ss123'
        tp = ui_lib.ui_driver(multihost)
        try:
            tp.setup()
            multihost.driver = tp
        except StandardError as errval:
            pytest.skip("setup_session_skip : %s" % (errval.args[0]))
        multihost.driver.init_app(username=user1, password=userpass)
        multihost.driver.logout()

    def test_rpm_version_0002(self, multihost):
        """
        test for automation of upgradation of packeges
        test for rpm comparison
        """
        rpm = "ipa-server"
        print "Current IPA version"
        ipa_version = get_rpm_version(multihost.master, rpm)                      # get current ipa version

        print ipa_version

        upgrade_from = '7.3.b'
        upgrade_to = '7.4.b'
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

        cmd = upgrade(multihost.master)  # upgrade starts at this point
        if cmd.returncode == 0:
            print("Upgraded Successfully")
        else:
            pytest.xfail("Upgrade Failed")

        updated_version = get_rpm_version(multihost.master, rpm)  # get updated ipa version
        print "Upgraded version is %s " % updated_version  # prints upgraded version

        if updated_version > ipa_version:
            print "Upgrade rpm test verified"
        else:
            pytest.xfail("rpm version check failed  on %s " % multihost.master)

    def test_logs_0003(self, multihost):
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

    def test_services_0004(self, multihost):
        """
        test for automation of upgradation of packeges
        test for service verification
        """
        multihost.master.kinit_as_admin()
        check_ipactl = multihost.master.run_command('ipactl status | grep RUNNING')
        if check_ipactl.returncode != 0:
            pytest.xfail("IPA server service not RUNNING.Kindly debug")
        else:
            print("IPA service is running, continuing")

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

    def test_webui_0006(self, multihost):
        """
        test for web ui testing after upgrade
        """
        user1 = 'testuser1'
        userpass = 'TestP@ss123'
        tp = ui_lib.ui_driver(multihost)
        try:
            tp.setup()
            multihost.driver = tp
        except StandardError as errval:
            pytest.skip("setup_session_skip : %s" % (errval.args[0]))
        multihost.driver.init_app(username=user1, password=userpass)
        multihost.driver.logout()

    def class_teardown(self, multihost):
        """Full suite teardown """
        pass
