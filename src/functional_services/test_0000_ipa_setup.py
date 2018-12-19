# pylint: disable=W0702
"""
:caselevel: Acceptance
:casecomponent: ipa
:caseautomation: Automated
:caseimportance: Critical
:testtype: Functional

Functional Services IPA Setup Tests
- This includes:
- master setup with ipa-server-install
- replica setup with ipa-replica-install
- client setup with ipa-client-install
- all use the shared library methods for installation
"""

from __future__ import print_function
import traceback
import pytest
from ipa_pytests.functional_services import setup_lib


class TestIpaSetup(object):
    """ IPA Install Tests for Functional Services test suite """
    fin = '/tmp/ipa_func_svcs_setup_ipa_env_done'
    def class_setup(self, multihost):
        """ Setup method for class...empty currently """
        pass

    def test_setup_ipa_master(self, multihost):
        """ :title: IPA-TC: Functional Services: Install IPA Master """
        if multihost.client.transport.file_exists(self.fin):
            print('Found finish file...skipping setup_master')
            return
        try:
            setup_lib.ipa_master(multihost)
        except:
            print(traceback.format_exc())
            multihost.client.put_file_contents(self.fin, 'failed')
            raise ValueError('Failed to setup IPA Master...exiting')

    def test_setup_ipa_replica(self, multihost):
        """ :title: IPA-TC: Functional Services: Install IPA Replica """
        if multihost.client.transport.file_exists(self.fin):
            print('Found finish file...skipping setup_replica')
            return
        try:
            setup_lib.ipa_replica(multihost)
        except:
            print(traceback.format_exc())
            multihost.client.put_file_contents(self.fin, 'failed')
            raise ValueError('Failed to setup IPA Replica...exiting')

    def test_setup_ipa_client(self, multihost):
        """ :title: IPA-TC: Functional Services: Install IPA Client """
        if multihost.client.transport.file_exists(self.fin):
            print('Found finish file...skipping setup_client')
            return
        try:
            setup_lib.ipa_client(multihost)
            multihost.client.put_file_contents(self.fin, 'x')
        except:
            print(traceback.format_exc())
            multihost.client.put_file_contents(self.fin, 'failed')
            raise ValueError('Failed to setup IPA Client...exiting')

    def class_teardown(self, multihost):
        """
        Teardown method for class
        Exit if any of the IPA setup failed
        """
        result = multihost.client.get_file_contents(self.fin,
                                                    encoding='utf-8')
        if 'failed' in result:
            pytest.exit('IPA ENV Setup Failed....exiting')
