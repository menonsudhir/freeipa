"""
This is a quick test for IPA Replica Promotion
"""
import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_install import (setup_replica, uninstall_server,
                                    setup_client)
from ipa_pytests.shared.user_utils import (add_ipa_user, del_ipa_user,
                                           show_ipa_user, find_ipa_user)
from ipa_pytests.shared.utils import (service_control, start_firewalld,
                                      stop_firewalld)
from ipa_pytests.shared.dns_utils import dns_record_add
from ipa_pytests.shared.host_utils import host_add, hostgroup_member_add
import time
import re


class TestIPAReplicaPromotion(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nUsing following hosts for IPA Replica Promotion testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("REPLICA: %s" % multihost.replica.hostname)
        print("*" * 80)

    def test_0001_replica_install_without_client(self, multihost):
        """
        IDM-IPA-TC: Installing IPA replica without IPA Client install
                    on given machine
        """
        multihost.master.kinit_as_admin()
        testuser = "test_0001_testuser1"
        passwd = multihost.master.config.admin_pw

        add_ipa_user(multihost.master, testuser, passwd)
        setup_replica(multihost.replica, multihost.master,
                      setup_dns=True,
                      setup_ca=True,
                      setup_reverse=True)
        cmd = show_ipa_user(multihost.replica, testuser)
        assert cmd.returncode == 0
        assert testuser in cmd.stdout_text
        if cmd.returncode == 0:
            # Try to uninstall if only we have successful replica install
            print("\nUninstalling IPA Replica server. Please wait ...")
            uninstall_server(multihost.replica)

    def test_0002_replica_install_without_required_params(self, multihost):
        """
        IDM-IPA-TC: Installing IPA replica without required parameters
        """
        cmd = "ipa-replica-install"
        cmdout = multihost.replica.run_command(cmd, raiseonerr=False)
        err_msg = "One of password / principal / keytab is required."
        assert err_msg in cmdout.stderr_text
        assert cmdout.returncode == 1

    def test_0003_replica_install_with_required_params(self, multihost):
        """
        IDM-IPA-TC: Installing IPA replica with required parameters
        """
        multihost.master.kinit_as_admin()
        testuser = "test_0003_testuser1"
        passwd = multihost.master.config.admin_pw

        add_ipa_user(multihost.master, testuser, passwd)
        setup_client(multihost.replica, multihost.master,
                     server=True, domain=True)
        print("\nInstalling IPA Replica using required parameters only")
        print("\nPlease wait")
        cmdstr = "ipa-replica-install -P admin -w {0}".format(passwd)
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        assert cmd.returncode == 0
        cmd = show_ipa_user(multihost.replica, testuser)
        assert cmd.returncode == 0
        assert testuser in cmd.stdout_text
        if cmd.returncode == 0:
            # Try to uninstall if only we have successful replica install
            print("\nUninstalling IPA Replica server. Please wait ...")
            uninstall_server(multihost.replica)

    def test_0004_prompt_replica_to_ca(self, multihost):
        """
        IDM-IPA-TC: Promoting IPA replica server with CA
        """
        multihost.master.kinit_as_admin()
        testuser = "test_0004_testuser1"
        passwd = multihost.master.config.admin_pw

        add_ipa_user(multihost.master, testuser, passwd)
        setup_replica(multihost.replica, multihost.master,
                      setup_dns=False,
                      setup_ca=False,
                      setup_reverse=True)
        cmd = show_ipa_user(multihost.replica, testuser)
        assert cmd.returncode == 0
        assert testuser in cmd.stdout_text

        # Add CA on replica
        multihost.replica.kinit_as_admin()
        cmdstr = "ipa-ca-install -P {0} -w {1}".format(passwd,
                                                       passwd)
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        cmdstr = "ipa server-role-find"
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        assert "{0}".format(multihost.replica.hostname) in cmd.stdout_text

        # Clean
        if cmd.returncode == 0:
            # Try to uninstall if only we have successful replica install
            print("\nUninstalling IPA Replica server. Please wait ...")
            uninstall_server(multihost.replica)

    def test_0005_kra_install(self, multihost):
        """
        IDM-IPA-TC: Installing KRA on IPA replica server
        """
        multihost.master.kinit_as_admin()
        testuser = "test_0005_testuser1"
        passwd = multihost.master.config.admin_pw

        add_ipa_user(multihost.master, testuser, passwd)
        setup_replica(multihost.replica, multihost.master,
                      setup_dns=True,
                      setup_ca=True,
                      setup_reverse=False)
        cmd = show_ipa_user(multihost.replica, testuser)
        assert cmd.returncode == 0
        assert testuser in cmd.stdout_text

        multihost.replica.kinit_as_admin()
        cmdstr = "ipa-kra-install"
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        cmdstr = "ipa server-role-find"
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        assert "{0}".format(multihost.replica.hostname) in cmd.stdout_text

        # Clean
        if cmd.returncode == 0:
            # Try to uninstall if only we have successful replica install
            print("\nUninstalling IPA Replica server. Please wait ...")
            uninstall_server(multihost.replica)

    def test_0006_rejoin_replica(self, multihost):
        """
        IDM-IPA-TC: Rejoin replica on given server after uninstall
        """
        multihost.master.kinit_as_admin()
        testuser = "test_0006_testuser1"
        passwd = multihost.master.config.admin_pw

        add_ipa_user(multihost.master, testuser, passwd)
        setup_replica(multihost.replica, multihost.master,
                      setup_dns=True,
                      setup_ca=True,
                      setup_reverse=False)
        cmd = show_ipa_user(multihost.replica, testuser)
        assert cmd.returncode == 0
        assert testuser in cmd.stdout_text

        uninstall_server(multihost.replica)

        setup_replica(multihost.replica, multihost.master,
                      setup_dns=True,
                      setup_ca=True,
                      setup_reverse=False)
        cmd = show_ipa_user(multihost.replica, testuser)
        assert cmd.returncode == 0
        assert testuser in cmd.stdout_text

        # Clean
        if cmd.returncode == 0:
            # Try to uninstall if only we have successful replica install
            print("\nUninstalling IPA Replica server. Please wait ...")
            uninstall_server(multihost.replica)

    def test_0007_otp_install(self, multihost):
        """
        IDM-IPA-TC: Installing IPA replica server using OTP token
        """
        multihost.master.kinit_as_admin()
        testuser = "test_0007_testuser1"
        passwd = multihost.master.config.admin_pw

        add_ipa_user(multihost.master, testuser, passwd)

        # Add DNS record for ipa host
        cmd = dns_record_add(multihost.master,
                             multihost.replica.domain.name,
                             multihost.replica.shortname,
                             'A',
                             [multihost.replica.ip])
        assert cmd.returncode == 0

        # Add host in host record
        cmd = host_add(multihost.master, multihost.replica.hostname,
                       options={'random': ''})
        assert cmd.returncode == 0
        result = re.search("Random password: (?P<password>.*$)",
                           cmd.stdout_text,
                           re.MULTILINE)
        randpasswd = result.group('password')
        # Add host to host group
        cmd = hostgroup_member_add(multihost.master, 'ipaservers',
                                   options={'hosts':
                                            multihost.replica.hostname})
        assert cmd.returncode == 0
        # Install replica using random password
        cmdstr = ['ipa-replica-install', '-p', randpasswd, '-U']
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        assert cmd.returncode == 0
        # Find out users on newly installed replica
        cmd = show_ipa_user(multihost.replica, testuser)
        assert cmd.returncode == 0
        assert testuser in cmd.stdout_text
        # Clean
        if cmd.returncode == 0:
            # Try to uninstall if only we have successful replica install
            print("\nUninstalling IPA Replica server. Please wait ...")
            uninstall_server(multihost.replica)

    def test_0008_otp_two_step_install(self, multihost):
        """
        IDM-IPA-TC: Installing IPA replica server using OTP installed client
        """
        multihost.master.kinit_as_admin()
        testuser = "test_0008_testuser1"
        passwd = multihost.master.config.admin_pw

        add_ipa_user(multihost.master, testuser, passwd)

        # Add DNS record for ipa host
        cmd = dns_record_add(multihost.master,
                             multihost.replica.domain.name,
                             multihost.replica.shortname,
                             'A',
                             [multihost.replica.ip])
        assert cmd.returncode == 0

        # Add host in host record
        cmd = host_add(multihost.master, multihost.replica.hostname,
                       options={'random': ''})
        assert cmd.returncode == 0
        result = re.search("Random password: (?P<password>.*$)",
                           cmd.stdout_text,
                           re.MULTILINE)
        randpasswd = result.group('password')
        # Add host to host group
        cmd = hostgroup_member_add(multihost.master, 'ipaservers',
                                   options={'hosts':
                                            multihost.replica.hostname})
        assert cmd.returncode == 0
        # Install client using random password
        cmdstr = ['ipa-client-install', '-w', randpasswd, '-U']
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        assert cmd.returncode == 0
        # Prompt client to REPLICA
        cmdstr = ['ipa-replica-install']
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        print("Stdout: %s" % cmd.stdout_text)
        print("Stderr: %s" % cmd.stderr_text)
        assert cmd.returncode == 0

        # Add CA on replica
        multihost.replica.kinit_as_admin()
        cmdstr = "ipa-ca-install -P {0} -w {1}".format(passwd,
                                                       passwd)
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        cmdstr = "ipa server-role-find"
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        assert "{0}".format(multihost.replica.hostname) in cmd.stdout_text

        # Find out users on newly installed replica
        cmd = show_ipa_user(multihost.replica, testuser)
        assert cmd.returncode == 0
        assert testuser in cmd.stdout_text
        # Clean
        if cmd.returncode == 0:
            # Try to uninstall if only we have successful replica install
            print("\nUninstalling IPA Replica server. Please wait ...")
            uninstall_server(multihost.replica)

    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Class teardown for IPA Replica Promotion")
        for i in xrange(1, 9):
            user = "test_000{0}_testuser1".format(i)
            cmd = find_ipa_user(multihost.master, user)
            if cmd.returncode == 0:
                print("\n Deleting IPA user {0}".format(user))
                cmd = del_ipa_user(multihost.master, user)
                if cmd.returncode != 0:
                    print("\nFailed to delete IPA user {0}"
                          "\nPlease do cleanup manually using "
                          "following command :".format(user))
                    print("\nipa user-del {0}".format(user))
