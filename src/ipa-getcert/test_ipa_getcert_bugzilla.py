'''
Test cases for IPA Getcert related bugzillas.
###############################################################
'''
import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_install import uninstall_server, setup_master
from ipa_pytests.shared import paths
from ipa_pytests.shared.utils import *

class Testmaster(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_bz1560961(self, multihost):
        """IDM-IPA-TC: ipa-getcert-pytest : Test to verify bz1560961"""
        setup_master(multihost.master)
        file1 = "/var/lib/certmonger/local/creds"
        file2 = "/tmp/ca.pem"
        if multihost.master.transport.file_exists(file1):
            cmd = multihost.master.run_command([paths.OPENSSL, 'pkcs12', '-in', file1, '-out', file2,
                                                '-nokeys', '-nodes', '-passin', 'pass:'],
                                     raiseonerr=False)
            print(cmd.stderr_text)
            print(cmd.stdout_text)
            if cmd.returncode != 0:
                pytest.xfail("Openssl command failed to create CA.PEM file.")
            print("Editing CA.pem file")
            cmd = multihost.master.run_command(['sed', '-i', '1,7d', file2],
                                     raiseonerr=False)
            print(cmd.stdout_text)
            cmd = multihost.master.run_command([paths.OPENSSL, 'asn1parse', '-in', file2,
                                               '-inform', 'pem'],
                                               raiseonerr=False)
            print(cmd.stderr_text)
            print(cmd.stdout_text)
            string = '30030101FF'
            if string in cmd.stdout_text:
                print('BZ1560961 verified successfully')
            else:
                pytest.fail('BZ1560961 verified successfully')

    def class_teardown(self, multihost):
        uninstall_server(multihost.master)
        pass
