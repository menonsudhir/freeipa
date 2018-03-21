"""
This is a cleanup module to undo everything the test did.
It should uninstall and reset configurations.
"""
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_install import uninstall_server


class TestCleanup(object):
    """ Cleanup Class """
    def test_setup(self, multihost):
        """ class level setup...should do nothing here """
        pass

    def test_teardown(self, multihost):
        """ Full suite teardown """
        multihost.master.kinit_as_admin()
        uninstall_server(multihost.master)
