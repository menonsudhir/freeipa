"""
Overview:
SetUp Requirements For IPA server upgrade
"""
import pytest
import time
from ipa_pytests.shared import paths
from selenium import webdriver
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.utils import ipa_version_gte
from ipa_pytests.qe_install import setup_master_ca_less, setup_replica_ca_less
from ipa_pytests.shared.user_utils import add_ipa_user, show_ipa_user
from ipa_pytests.test_webui import ui_lib
from ipa_pytests.shared.utils import run_pk12util
from ipa_pytests.shared.qe_certutils import certutil


class Testmaster(object):
    """ Test Class """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)
        master = multihost.master
        replica = multihost.replica
        passwd = 'Secret123'
        seconds = 10
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
        server2_subject = 'cn=%s' % replica.hostname

        certs = certutil(master, nssdb_dir)
        print("\n3. Creating self-signed CA certificate")
        if ipa_version_gte(master, '4.5.0'):
            certs.selfsign_cert(ca_subject, ca_nick, options=['-m', '1', '--extSKID'])
        else:
            certs.selfsign_cert(ca_subject, ca_nick, options=['-m', '1'])
        time.sleep(seconds)
        print("\n4. Creating self-signed server certificate")
        certs.create_server_cert(server_subject, server_nick, ca_nick)
        server_cert_file = '{}/server.p12'.format(nssdb_dir)

        print("\n5. Exporting certificates from database")
        if master.transport.file_exists(server_cert_file):
            master.run_command([paths.RM, '-rf', server_cert_file])

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
        cmd1 = setup_master_ca_less(multihost.master, passwd, passwd, passwd,
                                    server_cert_file, server_cert_file)
        print cmd1.stdout_text
        print cmd1.stderr_text

        replica_cert_file = '/root/replica.p12'
        certs.create_server_cert(server2_subject, 'replica', ca_nick)
        cmdstr2 = ['-o', replica_cert_file, '-n', 'replica', '-d',
                   nssdb_dir, '-k', certs.password_file, '-W', passwd]
        cmd = run_pk12util(master, cmdstr2)
        if cmd.returncode != 0:
            pytest.fail("Failed to export certificates from "
                        "nssdb [%s]" % nssdb_dir)
        else:
            print("\nSuccessfully exported certificate from nssdb "
                  "stored at [%s]" % replica_cert_file)

        cert_file = '/root/replica.p12'
        prep_content = master.get_file_contents(replica_cert_file)
        replica.put_file_contents(cert_file, prep_content)

        # Install CA-less replica
        cmd2 = setup_replica_ca_less(replica, master, passwd, passwd, passwd,
                                     cert_file, cert_file)
        print cmd2.stdout_text
        print cmd2.stderr_text

    def test_users_001(self, multihost):
        """IDM-IPA-TC : ca-less : Add and verify users on master and replica"""
        user1 = 'testuser1'
        userpass = 'TestP@ss123'
        add_ipa_user(multihost.master, user1, userpass)
        cmd = show_ipa_user(multihost.master, user1)
        assert cmd.returncode == 0

        cmd2 = show_ipa_user(multihost.replica, user1)
        assert cmd2.returncode == 0

    def test_web_ui0002(self, multihost):
        """
        IDM-IPA-TC : ca-less : Test for web ui for ca-less master
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

    def test_web_ui0003(self, multihost):
        """
        IDM-IPA-TC : ca-less : Test for web ui ca-less replica
        """
        user1 = 'testuser1'
        userpass = 'TestP@ss123'
        tp = ui_lib.ui_driver(multihost.replica)
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
