"""
Overview:
Test suite to verify ipa-advise output
"""

import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.qe_install import setup_master


class Testipaadvise(object):

    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_ipa_advise(self, multihost):
        """
        Test to verify Bugzilla 1353899 - ipa-advise
         object of type 'type' has no len()
        """
        setup_master(multihost.master)
        realm = multihost.master.domain.realm
        multihost.master.kinit_as_admin()
        exp_output = "Instructions for configuring a system"
        var1 = multihost.master.run_command(['ipa-advise'])

        if var1.stdout_text.find(exp_output):
            print("test_0001_ipa_advise verified")
        else:
            pytest.fail("bugzilla 1353899 found")

    def class_teardown(self, multihost):
        """ Class Teardown """
        pass
