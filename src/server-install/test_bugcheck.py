"""
Overview:
Test to verify Bugs:
#1283890
#1145584
#1196455
SetUp Requirements:
-Latest version of RHEL OS
-Need to test for Master
-The test use dummy data which is not used in actual installation.
"""

import pytest
from ipa_pytests.qe_install import setup_master, uninstall_server
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_use_class_setup


class Testmaster(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print"MASTER: ", multihost.master.hostname
        print("\nChecking IPA server whether installed on MASTER")
        output1 = multihost.master.run_command(['rpm', '-q', 'ipa-server'],
                                               set_env=False, raiseonerr=False)
        if output1.returncode == 0:
            print("IPA server package found on MASTER")
        else:
            print("\n IPA server package not found on MASTER, thus installing")
            install1 = multihost.master.run_command(['yum', 'install',
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
                pytest.xfail('IPA server package instalation failed, check',
                             'repo links for further debugging')
        uninstall_server(multihost.master)

    def test_0001_bz114584(self, multihost):
        check1 = multihost.master.run_command(['grep', 'pkiuser',
                                               '/etc/passwd',
                                               '&&', 'grep', 'pkiuser',
                                               '/etc/group'],
                                              set_env=False, raiseonerr=False)
        if check1.returncode != 0:
            print("pkiuser details not found, thus continuing")
        setup_master(multihost.master)
        check2 = multihost.master.run_command('grep pkiuser /etc/passwd && grep pkiuser /etc/group', raiseonerr=False)
        if check2.returncode != 0:
            print("pkiuser details not found, BZ114584 FAILED")
        else:
            print("pkiuser details found, BZ114584 PASSED")

    def test_0001_bz1196455(self, multihost):
        check3 = multihost.master.run_command('grep 300 /var/log/ipaserver-install.log')
        if check3.returncode == 0:
            print("300 second timeout message not found, continuing tests")
            check4 = multihost.master.run_command('openssl s_client -connect ' + multihost.master.hostname + ':8443', raiseonerr=False)
            if check4.returncode == 0:
                print('Client is able to connect, BZ1196455 PASSED')
            else:
                print('Client is unable to connect, BZ1196455 FAILED')
        else:
            print("300 second mesage found, BZ1196455 FAILED")

    def test_0001_bz1283890(self, multihost):
        uninstall_server(multihost.master)
        multihost.master.qerun(['ipa-server-install', '-a'],
                               exp_returncode=2,
                               exp_output="ipa-server-install: error: -a option")

    def test_0002_bz1283890(self, multihost):
        multihost.master.qerun(['ipa-server-install', '--setup-dns',
                                '--forwarder=10.11.5.19',
                                '-r', 'TESTRELM.TEST',
                                '-p', 'password', '-a', 'password',
                                '--zonemgr=Tko@redhat..com', '-U'],
                               exp_returncode=2,
                               exp_output="ipa-server-install: error: option --zonemgr: empty DNS label")

    def test_0003_bz1283890(self, multihost):
        multihost.master.qerun(['ipa-server-install', '--setup-dns',
                                '--forwarder=10.11.5.19', '-r TESTRELM.TEST',
                                '-p', 'password', '-a',
                                'password', '--subject'],
                               exp_returncode=2,
                               exp_output="ipa-server-install: error: --subject option requires an argument")

    def test_0004_bz1283890(self, multihost):
        multihost.master.qerun(['ipa-server-install', '--setup-dns',
                                '--forwarder=10.11.5.19', '-r TESTRELM.TEST',
                                '-p', 'password', '-a', 'password', '--subject=NOSUBJECT', '-U'],
                               exp_returncode=2,
                               exp_output="ipa-server-install: error: option --subject: invalid subject base format")

    def test_0005_bz1283890(self, multihost):
        multihost.master.qerun(['ipa-server-install', '--ip-address=a.b.3.4'],
                               exp_returncode=2,
                               exp_output="ipa-server-install: error: option --ip-address: invalid IP address")

    def test_0006_bz1283890(self, multihost):
        multihost.master.qerun(['ipa-server-install', '-xyz'],
                               exp_returncode=2,
                               exp_output="ipa-server-install: error: no such option")

    def class_teardown(self, multihost):
        """ Full suite teardown """
        pass
