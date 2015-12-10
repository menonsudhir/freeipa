"""
Overview:
Test to verify #1211589-[RFE] Add option to skip the verify_client_version
SetUp Requirements:
IPA Server configured on RHEL7.1
IPA Client configured on RHEL7.2
"""

import pytest
from ipa_pytests.qe_class import multihost


class Testipauserfind(object):

    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print "\nClass Setup"
        print "MASTER: ", multihost.master.hostname
        print "CLIENT: ", multihost.client.hostname

    def test_0001_ipauserfinderror(self, multihost):
        """
          IPA-TC: ipa user-find: ipa user-find gives
                  error when run on RHEL7.1 IPA client
        """
        realm = multihost.master.domain.realm
        multihost.client.kinit_as_admin()
        multihost.client.qerun(['ipa', 'user-find'], exp_returncode=1,
                               exp_output="ipa: ERROR:")

    def test_002_ipauserskipversioncheck(self, multihost):
        """
          IPA-TC: ipa user-find: ipa -e skip_version_check=1
                  user-find works without any error on RHEL7.1 client
        """
        realm = multihost.master.domain.realm
        multihost.client.kinit_as_admin()
        multihost.client.qerun(['ipa', '-e', 'skip_version_check=1',
                               'user-find'], exp_returncode=0,
                               exp_output="1 user matched")
