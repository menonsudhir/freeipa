"""
This is a quick test for IPA Replica Promotion
"""
import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_install import (setup_replica, uninstall_server,
                                    setup_client, set_etc_hosts)
from ipa_pytests.shared.user_utils import (add_ipa_user, del_ipa_user,
                                           show_ipa_user, find_ipa_user)
from ipa_pytests.shared.host_utils import host_add, hostgroup_member_add
from ipa_pytests.shared.server_utils import server_del
from ipa_pytests.shared.dns_utils import dns_record_add
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
        :Title: IDM-IPA-TC: Installing IPA replica without IPA Client install on given machine

        :Requirement: IDM-IPA-REQ : Replica Promotion

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        testuser = "test_0001_testuser1"
        passwd = multihost.master.config.admin_pw

        add_ipa_user(multihost.master, testuser, passwd)
        cmd = multihost.replica.run_command(['kdestroy', '-A'],
                                            raiseonerr=False)
        setup_replica(multihost.replica, multihost.master,
                      setup_dns=True,
                      setup_ca=True,
                      setup_reverse=False)
        cmd = show_ipa_user(multihost.replica, testuser)
        assert cmd.returncode == 0
        assert testuser in cmd.stdout_text
        if cmd.returncode == 0:
            # Try to uninstall if only we have successful replica install
            print("\nUninstalling IPA Replica server. Please wait ...")
            uninstall_server(multihost.replica)
            server_del(multihost.master,
                       hostname=multihost.replica.hostname,
                       force=True)

    def test_0002_replica_install_without_required_params(self, multihost):
        """
        :Title: IDM-IPA-TC: Installing IPA replica without required parameters

        :Requirement: IDM-IPA-REQ : Replica Promotion

        :Automation: Yes

        :casecomponent: ipa
        """
        cmd = "ipa-replica-install"
        cmdout = multihost.replica.run_command(cmd, raiseonerr=False)
        err_msg = "One of password / principal / keytab is required."
        assert err_msg in cmdout.stderr_text
        assert cmdout.returncode == 1

    def test_0003_replica_install_with_required_params(self, multihost):
        """
        :Title: IDM-IPA-TC: Installing IPA replica with required parameters

        :Requirement: IDM-IPA-REQ : Replica Promotion

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        testuser = "test_0003_testuser1"
        passwd = multihost.master.config.admin_pw

        add_ipa_user(multihost.master, testuser, passwd)
        cmd = multihost.replica.run_command(['kdestroy', '-A'],
                                            raiseonerr=False)
        setup_client(multihost.replica, multihost.master,
                     server=True, domain=True)
        print("\nInstalling IPA Replica using required parameters only")
        print("\nPlease wait...")
        cmd = multihost.replica.run_command(['kdestroy', '-A'],
                                            raiseonerr=False)
        set_etc_hosts(multihost.replica, multihost.master)
        set_etc_hosts(multihost.master, multihost.replica)
        cmdstr = "ipa-replica-install -U -P admin -w {0}".format(passwd)
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        print("Running    :> " + str (cmdstr))
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        assert cmd.returncode == 0
        cmd = show_ipa_user(multihost.replica, testuser)
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        assert cmd.returncode == 0
        assert testuser in cmd.stdout_text
        if cmd.returncode == 0:
            # Try to uninstall if only we have successful replica install
            print("\nUninstalling IPA Replica server. Please wait ...")
            uninstall_server(multihost.replica)
            server_del(multihost.master,
                       hostname=multihost.replica.hostname,
                       force=True)

    def test_0004_prompt_replica_to_ca(self, multihost):
        """
        :Title: IDM-IPA-TC: Promoting IPA replica server with CA

        :Requirement: IDM-IPA-REQ : Replica Promotion

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        testuser = "test_0004_testuser1"
        passwd = multihost.master.config.admin_pw

        add_ipa_user(multihost.master, testuser, passwd)
        cmd = multihost.replica.run_command(['kdestroy', '-A'],
                                            raiseonerr=False)
        setup_replica(multihost.replica, multihost.master,
                      setup_dns=True,
                      setup_ca=False,
                      setup_reverse=False)
        cmd = show_ipa_user(multihost.replica, testuser)
        assert cmd.returncode == 0
        assert testuser in cmd.stdout_text

        # Add CA on replica
        multihost.replica.kinit_as_admin()
        cmdstr = "ipa-ca-install -p {0} -w {1}".format(passwd,
                                                       passwd)
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        print("Running    :> " + str (cmdstr))
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        cmdstr = "ipa server-role-find"
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        print("Running    :> " + str (cmdstr))
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        assert "{0}".format(multihost.replica.hostname) in cmd.stdout_text

        # Clean
        if cmd.returncode == 0:
            # Try to uninstall if only we have successful replica install
            print("\nUninstalling IPA Replica server. Please wait ...")
            uninstall_server(multihost.replica)
            server_del(multihost.master,
                       hostname=multihost.replica.hostname,
                       force=True)

    def test_0005_kra_install(self, multihost):
        """
        :Title: IDM-IPA-TC: Installing KRA on IPA replica server

        :Requirement: IDM-IPA-REQ : Replica Promotion

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        testuser = "test_0005_testuser1"
        passwd = multihost.master.config.admin_pw

        add_ipa_user(multihost.master, testuser, passwd)
        cmd = multihost.replica.run_command(['kdestroy', '-A'],
                                            raiseonerr=False)
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
        print("Running    :> " + str (cmdstr))
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        cmdstr = "ipa server-role-find"
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        print("Running    :> " + str (cmdstr))
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        assert "{0}".format(multihost.replica.hostname) in cmd.stdout_text

        # Clean
        if cmd.returncode == 0:
            # Try to uninstall if only we have successful replica install
            print("\nUninstalling IPA Replica server. Please wait ...")
            uninstall_server(multihost.replica)
            server_del(multihost.master,
                       hostname=multihost.replica.hostname,
                       force=True)

    def test_0006_rejoin_replica(self, multihost):
        """
        :Title: IDM-IPA-TC: Rejoin replica on given server after uninstall

        :Requirement: IDM-IPA-REQ : Replica Promotion

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        testuser = "test_0006_testuser1"
        passwd = multihost.master.config.admin_pw

        add_ipa_user(multihost.master, testuser, passwd)
        cmd = multihost.replica.run_command(['kdestroy', '-A'],
                                            raiseonerr=False)
        setup_replica(multihost.replica, multihost.master,
                      setup_dns=True,
                      setup_ca=True,
                      setup_reverse=False)
        cmd = show_ipa_user(multihost.replica, testuser)
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        assert cmd.returncode == 0
        assert testuser in cmd.stdout_text
        
        uninstall_server(multihost.replica)
        server_del(multihost.master,
                       hostname=multihost.replica.hostname,
                       force=True)
        cmd = multihost.replica.run_command(['kdestroy', '-A'],
                                            raiseonerr=False)
        setup_replica(multihost.replica, multihost.master,
                      setup_dns=True,
                      setup_ca=True,
                      setup_reverse=False)
        cmd = show_ipa_user(multihost.replica, testuser)
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        assert cmd.returncode == 0
        assert testuser in cmd.stdout_text

        # Clean
        if cmd.returncode == 0:
            # Try to uninstall if only we have successful replica install
            print("\nUninstalling IPA Replica server. Please wait ...")
            uninstall_server(multihost.replica)
            server_del(multihost.master,
                       hostname=multihost.replica.hostname,
                       force=True)

    def test_0007_otp_install(self, multihost):
        """
        :Title: IDM-IPA-TC: Installing IPA replica server using OTP token

        :Requirement: IDM-IPA-REQ : Replica Promotion

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        testuser = "test_0007_testuser1"
        passwd = multihost.master.config.admin_pw

        uninstall_server(multihost.replica)
        add_ipa_user(multihost.master, testuser, passwd)
        cmd = multihost.replica.run_command(['kdestroy', '-A'],
                                            raiseonerr=False)
        # Add host in host record
        server_del(multihost.master,
                       hostname=multihost.replica.hostname,
                       force=True)
        cmd = dns_record_add(multihost.master,
                             multihost.master.domain.name,
                             multihost.replica.shortname,
                             'A',
                             [multihost.replica.ip])
        cmd = host_add(multihost.master, multihost.replica.hostname,
                       options={'random': ''})
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        assert cmd.returncode == 0
        result = re.search("Random password: (?P<password>.*$)",
                           cmd.stdout_text,
                           re.MULTILINE)
        print("result :>" + str(result))
        randpasswd = result.group('password')
        # Add host to host group
        cmd = hostgroup_member_add(multihost.master, 'ipaservers',
                                   options={'hosts':
                                            multihost.replica.hostname})
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        assert cmd.returncode == 0
        # Install replica using random password
        cmdstr = ['ipa-replica-install', '-p', randpasswd, '-U']
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        print("Running    :> " + str (cmdstr))
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        assert cmd.returncode == 0
        # Find out users on newly installed replica
        cmd = show_ipa_user(multihost.replica, testuser)
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        assert cmd.returncode == 0
        assert testuser in cmd.stdout_text
        # Clean
        if cmd.returncode == 0:
            # Try to uninstall if only we have successful replica install
            print("\nUninstalling IPA Replica server. Please wait ...")
            uninstall_server(multihost.replica)
            server_del(multihost.master,
                       hostname=multihost.replica.hostname,
                       force=True)

    def test_0008_otp_two_step_install(self, multihost):
        """
        :Title: IDM-IPA-TC: Installing IPA replica server using OTP installed client

        :Requirement: IDM-IPA-REQ : Replica Promotion

        :Automation: Yes

        :casecomponent: ipa
        """
        multihost.master.kinit_as_admin()
        testuser = "test_0008_testuser1"
        passwd = multihost.master.config.admin_pw

        uninstall_server(multihost.replica)
        add_ipa_user(multihost.master, testuser, passwd)

        # Add host in host record
        server_del(multihost.master,
                       hostname=multihost.replica.hostname,
                       force=True)
        cmd = dns_record_add(multihost.master,
                             multihost.master.domain.name,
                             multihost.replica.shortname,
                             'A',
                             [multihost.replica.ip])
        cmd = host_add(multihost.master, multihost.replica.hostname,
                       options={'random': ''})
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        assert cmd.returncode == 0
        result = re.search("Random password: (?P<password>.*$)",
                           cmd.stdout_text,
                           re.MULTILINE)
        print("result :> " + str(result))
        randpasswd = result.group('password')
        # Add host to host group
        cmd = hostgroup_member_add(multihost.master, 'ipaservers',
                                   options={'hosts':
                                            multihost.replica.hostname})
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        assert cmd.returncode == 0
        # Install client using random password
        cmd = multihost.replica.run_command(['kdestroy', '-A'],
                                            raiseonerr=False)
        cmdstr = ['ipa-client-install', '-w', randpasswd, '-U']
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        print("Running    :> " + str (cmdstr))
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        assert cmd.returncode == 0
        # Prompt client to REPLICA
        cmd = multihost.replica.run_command(['kdestroy', '-A'],
                                            raiseonerr=False)
        cmdstr = ['ipa-replica-install', '-U']
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        print("Stdout: %s" % cmd.stdout_text)
        print("Stderr: %s" % cmd.stderr_text)
        assert cmd.returncode == 0

        # Add CA on replica
        cmd = multihost.replica.run_command(['kdestroy', '-A'],
                                            raiseonerr=False)
        multihost.replica.kinit_as_admin()
        cmdstr = "ipa-ca-install -p {0} -w {1}".format(passwd,
                                                       passwd)
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        print("Running    :> " + str (cmdstr))
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        cmdstr = "ipa server-role-find"
        cmd = multihost.replica.run_command(cmdstr, raiseonerr=False)
        print("Running    :> " + str (cmdstr))
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        assert "{0}".format(multihost.replica.hostname) in cmd.stdout_text

        # Find out users on newly installed replica
        cmd = show_ipa_user(multihost.replica, testuser)
        print("CMD STDOUT :> " + cmd.stdout_text)
        print("CMD STDERR :> " + cmd.stderr_text)
        assert cmd.returncode == 0
        assert testuser in cmd.stdout_text
        # Clean
        if cmd.returncode == 0:
            # Try to uninstall if only we have successful replica install
            print("\nUninstalling IPA Replica server. Please wait ...")
            uninstall_server(multihost.replica)
            server_del(multihost.master,
                       hostname=multihost.replica.hostname,
                       force=True)

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

