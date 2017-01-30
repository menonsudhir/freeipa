"""
Testsuite for IPA Lightweight Sub CA - ca-add
"""
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.ca_utils import *
from ipa_pytests.shared.utils import *
from lib import *
import pexpect
import pytest
import re
import time


class TestSubCAAdd(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nUsing following hosts for IPA Lightweight Sub-CA testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("REPLICA: %s" % multihost.replica.hostname)
        print("*" * 80)

    def test_0001_subca_add_help(self, multihost):
        """
        test_0001_subca_add_help
        IDM-IPA-TC: ipa ca add with help option
        """
        multihost.master.kinit_as_admin()
        cmd = "ipa help ca-add"
        print("Running : {0}".format(cmd))
        cmdout = multihost.master.run_command(cmd, raiseonerr=False)
        assert "Usage: ipa [global-options] " \
               "ca-add NAME [options]" in cmdout.stdout_text
        assert "Create a CA." in cmdout.stdout_text
        cmd = "ipa ca-add --help"
        print("Running : {0}".format(cmd))
        cmdout = multihost.master.run_command(cmd, raiseonerr=False)
        assert "Usage: ipa [global-options] " \
               "ca-add NAME [options]" in cmdout.stdout_text
        assert "Create a CA." in cmdout.stdout_text

    def test_0002_subca_add_subca(self, multihost):
        """
        test_0002_subca_add_subca
        IDM-IPA-TC: ipa ca add with options
        """
        multihost.master.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0002_subca1"
        subca['description'] = subca['name']
        subca['realm'] = multihost.realm
        # Add new Sub CA
        cmd = ca_add(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_add_output(subca, cmd[1])
        # Find new Sub CA
        cmd = ca_find(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_find_output(subca, cmd[1])
        # Delete create Sub CA
        cmd = ca_del(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_del_output(subca, cmd[1])

    def test_0003_subca_add_interactive(self, multihost):
        """
        test_0003_subca_add_interactive
        IDM-IPA-TC: ipa ca add in interactive mode
        """
        multihost.master.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0003_subca1"
        subca['realm'] = multihost.realm
        # Add Sub CA
        cmd = "ipa ca-add"
        print("Running : {0}".format(cmd))
        events = {"Name: ": '{0}\n'.format(subca['name']),
                  "Subject DN: ": "CN={0},O={1}\n".format(subca['name'],
                                                          subca['realm'])}
        cmdout = pexpect.run(cmd, events=events)
        check_ca_add_output(subca, cmdout)
        # Delete create Sub CA
        cmd = ca_del(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_del_output(subca, cmd[1])

    def test_0004_subca_add_existing_subca(self, multihost):
        """
        test_0004_subca_add_existing_subca
        IDM-IPA-TC: ipa ca add with pre-existing Sub CA name
        """
        multihost.master.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0004_subca1"
        subca['realm'] = multihost.realm
        # Add Sub CA
        cmd = ca_add(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_add_output(subca, cmd[1])
        # Find Sub CA
        cmd = ca_find(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_find_output(subca, cmd[1])
        # Create existing Sub CA
        cmd = ca_add(multihost.master, subca)
        assert "Certificate Authority with name \"{0}\" " \
               "already exists".format(subca['name']) in cmd[2]
        # Delete create Sub CA
        cmd = ca_del(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_del_output(subca, cmd[1])

    def test_0005_subca_add_existing_subjectDN(self, multihost):
        """
        test_0005_subca_add_existing_subjectDN
        IDM-IPA-TC: ipa ca add with pre-existing Subject DN
        """
        multihost.master.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0005_subca1"
        subca['cname'] = subca['name'] + " Sub CA"
        subca['realm'] = multihost.realm
        # Add new Sub CA
        cmd = ca_add(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_add_output(subca, cmd[1])
        # Find Sub CA
        cmd = ca_find(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_find_output(subca, cmd[1])
        # Create existing Sub CA with Subject DN
        cmd = ca_add(multihost.master, subca)
        assert "Certificate Authority " \
               "with name \"{0}\" " \
               "already exists".format(subca['name']) in cmd[2]
        # Delete create Sub CA
        cmd = ca_del(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_del_output(subca, cmd[1])

    def test_0006_subca_issue_certificates(self, multihost):
        """
        test_0006_subca_issue_certificates
        IDM-IPA-TC: Issue certificate using Sub CA
        """
        multihost.master.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0006_subca1"
        subca['realm'] = multihost.realm
        # Add Sub CA
        cmd = ca_add(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_add_output(subca, cmd[1])

        # Find Sub CA
        cmd = ca_find(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_find_output(subca, cmd[1])

        # Find CA ACL Policy
        subca_acl = {}
        subca_acl['name'] = "hosts_services_caIPAserviceCert"
        cmd = ca_acl_find(multihost.master, subca_acl)
        assert "ACL name: {0}".format(subca_acl['name']) in cmd[1]

        # Add CA ACL policy
        subca_acl['subca'] = subca['name']
        cmd = ca_acl_add_ca(subca_acl)
        assert "ACL name: {0}".format(subca_acl['name']) in cmd[1]

        # Create temp directory
        tempdir_name = "/tmp/temp_{0}".format(subca['name'])
        mkdtemp(multihost.master, tempdir_name)

        # Change SELinux context for temp directory
        chcon(multihost.master, 'cert_t', tempdir_name)

        # Issue certificate using newly creates Sub CA
        cmd = "ipa-getcert request " \
              "-k {0}/{1}_file.key " \
              "-f {2}/{3}_file.pem " \
              "-X {4}".format(tempdir, subca['name'],
                              tempdir, subca['name'],
                              subca['name'])
        print("Running : {0}".format(cmd))
        cmdout = multihost.master.run_command(cmd, raiseonerr=False)
        assert "added." in cmdout.stdout_text
        request_regex = re.compile("New signing request \"(.*)\" added.")
        request_num = re.match(request_regex, cmdout.stdout_text).group(1)
        assert request_num

        # Sleep for some time
        seconds = 20
        print("Sleeping for {0} seconds".format(seconds))
        time.sleep(seconds)

        # Get list of all cert and find required certificate
        cmd = "ipa-getcert list -i {0}".format(request_num)
        print("Running : {0}".format(cmd))
        cmdout = multihost.master.run_command(cmd, raiseonerr=False)
        assert "Request ID '{0}'".format(request_num) in cmdout.stdout_text
        assert "status: MONITORING" in cmdout.stdout_text
        assert "stuck: no" in cmdout.stdout_text
        assert "CA: IPA" in cmdout.stdout_text
        assert "issuer: " \
               "CN={0},O={1}".format(subca['name'],
                                     multihost.realm) in cmdout.stdout_text

        # Clean up
        cmd = "ipa-getcert stop-tracking -i {0}".format(request_num)
        print("Running : {0}".format(cmd))
        cmdout = multihost.master.run_command(cmd, raiseonerr=False)
        assert "Request \"{0}\" " \
               "removed.".format(request_num) in cmdout.stdout_text

        # Delete temp directory
        cmd = "rm -rf {0}".format(tempdir)
        print("Running : {0}".format(cmd))
        cmdout = multihost.master.run_command(cmd, raiseonerr=False)

        # Delete create Sub CA
        cmd = ca_del(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_del_output(subca, cmd[1])

    def test_0007_subca_issue_certificates_replica(self, multihost):
        """
        test_0007_subca_issue_certificates_replica
        IDM-IPA-TC: Issue certificate using Sub CA from replica
        """
        multihost.replica.kinit_as_admin()
        subca = {}
        subca['name'] = "test_0007_subca1"
        subca['realm'] = multihost.realm

        # Find CA ACL Policy
        acl = "hosts_services_caIPAserviceCert"
        cmd = "ipa caacl-find {0}".format(acl)
        print("Running : {0}".format(cmd))
        cmdout = multihost.replica.run_command(cmd, raiseonerr=False)
        assert "ACL name: {0}".format(acl) in cmdout.stdout_text

        # Add new Sub CA
        cmd = ca_add(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_add_output(subca, cmd[1])

        # Find Sub CA
        cmd = ca_find(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_find_output(subca, cmd[1])

        # Add CA ACL policy
        cmd = "ipa caacl-add-ca {0} --cas={1}".format(acl, subca['name'])
        print("Running : {0}".format(cmd))
        cmdout = multihost.replica.run_command(cmd, raiseonerr=False)
        assert "ACL name: {0}".format(acl) in cmdout.stdout_text

        # Create temp directory
        tempdir = "/tmp/temp_{0}".format(subca['name'])
        cmd = "mkdir {0}".format(tempdir)
        print("Running : {0}".format(cmd))
        cmdout = multihost.replica.run_command(cmd, raiseonerr=False)

        # Change SELinux context for temp directory
        cmd = "chcon -t cert_t {0}".format(tempdir)
        print("Running : {0}".format(cmd))
        cmdout = multihost.replica.run_command(cmd, raiseonerr=False)

        # Issue certificate using newly creates Sub CA
        cmd = "ipa-getcert request " \
              "-k {0}/{1}_file.key " \
              "-f {2}/{3}_file.pem " \
              "-X {4}".format(tempdir, subca['name'],
                              tempdir, subca['name'],
                              subca['name'])
        cmdout = multihost.replica.run_command(cmd, raiseonerr=False)
        print("Running : {0}".format(cmd))
        assert "added." in cmdout.stdout_text
        request_regex = re.compile("New signing request \"(.*)\" added.")
        request_num = re.match(request_regex, cmdout.stdout_text).group(1)
        assert request_num
        print("Certificate \"{0}\" found".format(request_num))

        # Sleep for some time
        seconds = 20
        print("Sleeping for {0} seconds".format(seconds))
        time.sleep(seconds)

        cmd = "ipa-getcert list -i {0}".format(request_num)
        print("Running : {0}".format(cmd))
        cmdout = multihost.replica.run_command(cmd, raiseonerr=False)
        assert "Request ID '{0}'".format(request_num) in cmdout.stdout_text
        assert "status: MONITORING" in cmdout.stdout_text
        assert "stuck: no" in cmdout.stdout_text
        assert "CA: IPA" in cmdout.stdout_text
        assert "issuer: " \
               "CN={0},O={1}".format(subca['name'],
                                     multihost.realm) in cmdout.stdout_text

        # Clean up
        cmd = "ipa-getcert stop-tracking -i {0}".format(request_num)
        print("Running : {0}".format(cmd))
        cmdout = multihost.replica.run_command(cmd, raiseonerr=False)
        assert "Request \"{0}\" " \
               "removed.".format(request_num) in cmdout.stdout_text

        cmd = "rm -rf {0}".format(tempdir)
        print("Running : {0}".format(cmd))
        cmdout = multihost.replica.run_command(cmd, raiseonerr=False)

        # Delete create Sub CA
        cmd = ca_del(multihost.master, subca)
        if cmd[0] == 0:
            check_ca_del_output(subca, cmd[1])

    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Class teardown for Sub CA")
