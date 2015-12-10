"""
This is a cleanup module to undo everything the test did.
It should uninstall and reset configurations.
"""


class TestCleanup(object):
    """ Cleanup Class """
    def test_setup(self, multihost):
        """ class level setup...should do nothing here """
        pass

    def test_teardown(self, multihost):
        """ Full suite teardown """
        multihost.master.kinit_as_admin()
        multihost.master.run_command(['ipa-server-install',
                                     '--uninstall', '-U'])
        multihost.client.kinit_as_admin()
        multihost.client.run_command(['ipa-client-install', '--uninstall'])
