"""
Overview:
IPA server install bz automation
SetUp Requirements:
-Latest version of RHEL OS
-Need to test for Master
-The test use dummy data which is not used in actual installation.
"""

import time
import pytest
from ipa_pytests.qe_install import setup_master, uninstall_server
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.shared import paths
from ipa_pytests.shared.qe_certutils import certutil
from ipa_pytests.shared.utils import run_pk12util
from ipa_pytests.shared.user_utils import add_ipa_user, del_ipa_user
from ipa_pytests.shared.utils import get_domain_level
from ipa_pytests.shared.utils import (start_firewalld,
                                      stop_firewalld)


class Testmaster(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print("MASTER: %s" % multihost.master.hostname)
        print("REPLICA: %s" % multihost.replicas[0].hostname)
        print("\nChecking IPA server whether installed on MASTER")
        output1 = multihost.master.run_command([paths.RPM, '-q', 'ipa-server'],
                                               set_env=False, raiseonerr=False)
        if output1.returncode == 0:
            print("IPA server package found on MASTER")
        else:
            print("\n IPA server package not found on MASTER, thus installing")
            install1 = multihost.master.run_command([paths.YUM, 'install',
                                                     '-y',
                                                     'ipa-server*'])
            if install1.returncode == 0:
                print("IPA server package installed.")
                install2 = multihost.master.run_command('ipactl status | grep',
                                                        'RUNNING')
                if install2.returncode != 0:
                    print("IPA server service not RUNNING.")
                else:
                    print("IPA service is running, need to uninstall")
            else:
                pytest.fail('IPA server package installation failed, check',
                            'repo links for further debugging')
        uninstall_server(multihost.master)

    def test_0001_bz114584(self, multihost):
        """
        Validating pkiuser existence after IPA installation
        """
        check1 = multihost.master.run_command(['grep', 'pkiuser',
                                               '/etc/passwd',
                                               '&&', 'grep', 'pkiuser',
                                               '/etc/group'],
                                              set_env=False, raiseonerr=False)
        if check1.returncode != 0:
            print("pkiuser details not found, thus continuing")
        setup_master(multihost.master)
        check2 = multihost.master.run_command('grep pkiuser /etc/passwd '
                                              '&& grep pkiuser /etc/group',
                                              raiseonerr=False)
        if check2.returncode != 0:
            print("pkiuser details not found, BZ114584 FAILED")
        else:
            print("pkiuser details found, BZ114584 PASSED")

    def test_0002_bz1196455(self, multihost):
        """
        Validating client cert connection with IPA server
        """
        cmdstr = 'grep 300 /var/log/ipaserver-install.log'
        check3 = multihost.master.run_command(cmdstr)
        if check3.returncode == 0:
            print("300 second timeout message not found, continuing tests")
            cmdstr = 'openssl s_client -connect ' + multihost.master.hostname + \
                     ':8443'
            check4 = multihost.master.run_command(cmdstr, raiseonerr=False)
            if check4.returncode == 0:
                print('Client is able to connect, BZ1196455 PASSED')
            else:
                print('Client is unable to connect, BZ1196455 FAILED')
        else:
            print("300 second mesage found, BZ1196455 FAILED")

    def test_0003_bz1283890(self, multihost):
        """
        Testcase to validate IPA server install parameters
        """
        uninstall_server(multihost.master)
        multihost.master.qerun(['ipa-server-install', '-a'],
                               exp_returncode=2,
                               exp_output="ipa-server-install: error: "
                                          "-a option")

    def test_0004_bz1283890(self, multihost):
        """
        Testcase to validate IPA server install parameters
        """
        multihost.master.qerun(['ipa-server-install', '--setup-dns',
                                '--forwarder=10.11.5.19',
                                '-r', 'TESTRELM.TEST',
                                '-p', 'password', '-a', 'password',
                                '--zonemgr=Tko@redhat..com', '-U'],
                               exp_returncode=2,
                               exp_output="ipa-server-install: error: "
                                          "option zonemgr: empty DNS label")

    def test_0005_bz1283890(self, multihost):
        """
        Testcase to validate IPA server install parameters
        """
        exp_output = "ipa-server-install: error: --subject option " \
                     "requires an argument"
        multihost.master.qerun(['ipa-server-install', '--setup-dns',
                                '--forwarder=10.11.5.19', '-r TESTRELM.TEST',
                                '-p', 'password', '-a',
                                'password', '--subject'],
                               exp_returncode=2,
                               exp_output=exp_output)

    def test_0006_bz1283890(self, multihost):
        """
        Testcase to validate IPA server install parameters
        """
        exp_output = "ipa-server-install: error: option --subject: " \
                     "invalid subject base format"
        multihost.master.qerun(['ipa-server-install', '--setup-dns',
                                '--forwarder=10.11.5.19', '-r TESTRELM.TEST',
                                '-p', 'password', '-a', 'password',
                                '--subject=NOSUBJECT', '-U'],
                               exp_returncode=2,
                               exp_output=exp_output)

    def test_0007_bz1283890(self, multihost):
        """
        Testcase to validate IPA server install parameters
        """
        exp_output = "ipa-server-install: error: option " \
                     "--ip-address: invalid IP address"
        multihost.master.qerun(['ipa-server-install', '--ip-address=a.b.3.4'],
                               exp_returncode=2,
                               exp_output=exp_output)

    def test_0008_bz1283890(self, multihost):
        """
        Testcase to validate IPA server install parameters
        """
        exp_output = "ipa-server-install: error: no such option"
        multihost.master.qerun(['ipa-server-install', '-xyz'],
                               exp_returncode=2,
                               exp_output=exp_output)

    def test_0009_bz1324060(self, multihost):
        """
        test_0010_bz1324060
        Verify ipa-server and ipa-replica installation using self-signed CA
        and self-signed server certificates
        """

        master1 = multihost.master
        replica1 = multihost.replicas[0]
        print("Using following hosts for test")
        print("*" * 80)
        print("Master : %s" % master1.hostname)
        print("Replica: %s" % replica1.hostname)
        print("*" * 80)
        passwd = 'Secret123'
        seconds = 10
        """Adding command to stop firewall service on master and replica"""
        stop_firewalld(multihost.master)
        stop_firewalld(multihost.replicas[0])

        # Check IPA server rpm version
        print("\n1. checking IPA server rpm version")
        cmdstr = "rpm -q ipa-server"
        for machine in [master1, replica1]:
            cmd = machine.run_command(cmdstr, raiseonerr=False)
            if cmd.returncode != 0:
                pytest.fail("Failed to run [%s] on machine [%s]"
                            % (cmdstr, machine.hostname))
            else:
                print("IPA server package installed on [%s] :\n[%s]"
                      % (machine.hostname, cmd.stdout_text.strip()))

        # Create tmp directory
        nssdb_dir = '/tmp/nssdb'
        if master1.transport.file_exists(nssdb_dir):
            cmd = master1.run_command([paths.RM, '-rf', nssdb_dir],
                                      raiseonerr=False)
            if cmd.returncode != 0:
                pytest.fail("Failed to remove directory %s" % nssdb_dir)

        print("\n2. Creating nss database at [%s]" % nssdb_dir)
        ca_nick = 'ca'
        ca_subject = "cn=Test_CA"

        server_nick = 'server'
        server_subject = 'cn=%s' % master1.hostname

        certs = certutil(master1, nssdb_dir)
        print("\n3. Creating self-signed CA certificate")
        certs.selfsign_cert(ca_subject, ca_nick, options=['-m', '1'])

        print("\nSleeping for [%d] seconds" % seconds)
        time.sleep(seconds)
        print("\n4. Creating self-signed server certificate")
        certs.create_server_cert(server_subject, server_nick, ca_nick)

        # Export certificates
        server_cert_file = '{}/server.p12'.format(nssdb_dir)

        print("\n5. Exporting certificates from database")
        if master1.transport.file_exists(server_cert_file):
            master1.run_command([paths.RM, '-rf', server_cert_file],
                                raiseonerr=False)

        cmdstr = ['-o', server_cert_file, '-n', 'server', '-d',
                  nssdb_dir, '-k', certs.password_file, '-W', passwd]
        cmd = run_pk12util(master1, cmdstr)
        if cmd.returncode != 0:
            pytest.fail("Failed to export certificates from "
                        "nssdb [%s]" % nssdb_dir)
        else:
            print("\nSuccessfully exported certificate from nssdb "
                  "stored at [%s]" % server_cert_file)
        # Install ipa-server using self-signed CA and Server certificates
        print("\n6. Installing ipa-server using self-signed CA and "
              "Server certificate")
        cmdstr = "ipa-server-install --http-cert-file {} " \
                 "--dirsrv-cert-file {} --ip-address {} -r {} -p {} " \
                 "-a {} --setup-dns --forwarder {} --http-pin {} " \
                 "--dirsrv-pin {} -U".format(server_cert_file,
                                             server_cert_file,
                                             master1.ip,
                                             master1.domain.realm,
                                             passwd, passwd,
                                             master1.config.dns_forwarder,
                                             passwd, passwd)
        print("\nRuning command : %s" % cmdstr)
        cmd = master1.run_command(cmdstr, raiseonerr=False)
        if cmd.returncode != 0:
            print(cmd.stdout_text, cmd.stderr_text)
            pytest.fail("Failed to install IPA server on machine [%s]"
                        % master1.hostname)
        else:
            print("\nIPA server installed successfully")

        # Update CA certificate in nssdb
        print("\n7. Update self-signed CA certificate in nssdb")
        certs.selfsign_cert(ca_subject, ca_nick, options=['-m', '3',
                                                          '-k', 'ca'])
        print("\nSleeping for [%d] seconds" % seconds)
        time.sleep(seconds)

        # Create Replica certificate in nssdb
        print("\n8. Create self-signed replica certifcate")
        replica_subject = 'cn=%s' % replica1.hostname
        replica_nick = 'replica'

        opts = ['-m', '4']
        certs.create_server_cert(replica_subject, replica_nick,
                                 ca_nick, options=opts)
        # Export certificates
        replica_cert_file = '{}/replica.p12'.format(nssdb_dir)
        print("\n9. Exporting replica certificates from database")
        if master1.transport.file_exists(replica_cert_file):
            master1.run_command([paths.RM, '-rf', replica_cert_file],
                                raiseonerr=False)

        cmdstr = ['-o', replica_cert_file, '-n', 'replica', '-d',
                  nssdb_dir, '-k', certs.password_file, '-W', passwd]
        cmd = run_pk12util(master1, cmdstr)
        if cmd.returncode != 0:
            print(cmd.stdout_text, cmd.stderr_text)
            pytest.fail("Failed to export replica certificate from "
                        "nssdb [%s]" % nssdb_dir)
        else:
            print("Successfully exported replica certificate from nssdb "
                  "stored at [%s]" % replica_cert_file)

        domain_level = get_domain_level(master1)

        if domain_level == 0:
            print ("Domain Level is 0 so we have to use prepare files")

            # Create replica file
            print("\n10. Creating replica file")
            tmp_file = "/var/lib/ipa/replica-info-{}.gpg".format(
                replica1.hostname)
            if master1.transport.file_exists(tmp_file):
                print("Previously created replica GPG file exists "
                      "on %s, deleting..." % master1.hostname)
                master1.run_command([paths.RM, '-rf', tmp_file],
                                    raiseonerr=False)

            reverse_zone = replica1.ip.split(".")[:-1]
            reverse_zone.reverse()
            replica_reverse_zone = ".".join(reverse_zone) + '.in-addr.arpa.'
            cmdstr = "ipa-replica-prepare {} --http-cert-file={} " \
                     "--http-pin {} " \
                     "--dirsrv-cert-file={} --dirsrv-pin {} --ip-address {} " \
                     "--reverse-zone {}".format(replica1.hostname,
                                                replica_cert_file,
                                                passwd, replica_cert_file,
                                                passwd, replica1.ip,
                                                replica_reverse_zone)

            print("Running command : %s" % cmdstr)
            cmd = master1.run_command(cmdstr, stdin_text=passwd,
                                      raiseonerr=False)
            if cmd.returncode != 0:
                print(cmd.stdout_text, cmd.stderr_text)
                pytest.fail("Failed to prepare replica file")
            else:
                print("Successfully created replica file")

            replica_prep_file = '/tmp/replica-info-{}.gpg'.format(
                replica1.hostname)
            print("Copying %s to %s server" %
                  (replica_prep_file, replica1.hostname))
            if replica1.transport.file_exists(replica_prep_file):
                print("Previously created replica GPG file exists, deleting...")
                replica1.run_command([paths.RM, '-rf', replica_prep_file],
                                     raiseonerr=False)

            cmdstr = 'scp {} root@{}:{}'.format(tmp_file,
                                                replica1.hostname,
                                                replica_prep_file)
            print("\nRunning command %s" % cmdstr)
            cmd = master1.run_command(cmdstr, raiseonerr=False)

            if not replica1.transport.file_exists(replica_prep_file):
                print(cmd.stdout_text, cmd.stderr_text)
                pytest.fail("Failed to copy %s to %s "
                            "server" % (tmp_file, replica1.hostname))
        else:
            cmd = replica1.run_command(['mkdir', '-p', '/tmp/nssdb'],
                                       raiseonerr=False)
            replica_cert_content = master1.get_file_contents(replica_cert_file)
            replica1.put_file_contents(replica_cert_file, replica_cert_content)

        # Create IPA user
        username = 'testuser1'
        print("\n11. Adding IPA user [%s]" % username)
        master1.kinit_as_admin()
        add_ipa_user(master1, username, passwd)

        # Install replica
        print("\n12. Installing replica on server [%s] " % replica1.hostname)
        cmdstr = ['ipa-replica-install',
                  '--setup-dns',
                  '--no-forwarders',
                  '--admin-password', passwd,
                  '--mkhomedir']

        if domain_level == 0:
            cmdstr += [replica_prep_file, '--password', passwd]
        else:
            cmdstr += ['--server', master1.hostname,
                       '--domain', master1.domain.realm,
                       '--http-cert-file', replica_cert_file,
                       '--http-pin', passwd,
                       '--dirsrv-cert-file', replica_cert_file,
                       '--dirsrv-pin', passwd,
                       '--allow-zone-overlap']

        cmdstr += ['--ip-address', replica1.ip,
                   '--unattended']

        print("\nRunning command : %s" % " ".join(cmdstr))
        cmd = replica1.run_command(cmdstr, raiseonerr=False)
        if cmd.returncode != 0:
            print(cmd.stdout_text, cmd.stderr_text)
            pytest.fail("Failed to install replica "
                        "on [%s]" % replica1.hostname)
        else:
            print("\nSuccessfully installed replica "
                  "on [%s]" % replica1.hostname)

        # Kinit as user
        replica1.kinit_as_user(username, passwd)
        print("\n13. Check IPA user on replica [%s]" % replica1.hostname)
        cmd = replica1.run_command(paths.KLIST, raiseonerr=False)
        if cmd.returncode != 0:
            print(cmd.stdout_text, cmd.stderr_text)
            pytest.fail("Failed to run klist for user [%s]" % username)
        else:
            print("\nSuccessfully verified BZ#1324060")

        print("\nTeardown for ipa-server-install BZ#1324060")
        print("\nDeleting user [%s]" % username)
        del_ipa_user(master1, username)
        # Delete tmp directory
        if master1.transport.file_exists(nssdb_dir):
            master1.run_command([paths.RM, '-rf', nssdb_dir],
                                raiseonerr=False)

    def test_0010_bz1200883(self, multihost):
        """
        This is to check that mod_auth_gssapi now being used with IPA instead of
        mod_auth_kerb
        """
        uninstall_server(multihost.master)
        setup_master(multihost.master)
        url = "https://" + multihost.master.hostname + "/ipa/"
        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['curl', '-v', '--negotiate', '-u:', url],
                                           raiseonerr=False)

        print cmd.stderr_text
        if 'mod_auth_gssapi' in cmd.stderr_text:
            print "IPA server using mod_auth_gssapi instead of mod_auth_kerb"
        else:
            pytest.xfail("mod_auth_gssapi not used by IPA server")

        print cmd.stdout_text
        if '404 Not Found' in cmd.stdout_text:
            print "Expected output found"
        else:
            pytest.xfail("Expected output not found")

    def class_teardown(self, multihost):
        """ Full suite teardown """
        pass
