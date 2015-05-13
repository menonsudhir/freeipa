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
        multihost.client.kinit_as_admin()
        multihost.client.run_command(['remove-ds.pl', '-i', 'slapd-instance1'])
        multihost.client.run_command(['rm', '-f', '/etc/dirsrv/ldap_service.keytab'])
        multihost.client.run_command(['ipa', 'service-del', 'ldap/' + multihost.client.hostname])
        multihost.client.run_command(['ipa', 'user-del', 'ldapuser1'])

#        multihost.client.run_command(['ipa', 'service-del', 'HTTP/' + multihost.client.hostname])
#        multihost.client.run_command(['ipa', 'user-del', 'httpuser1'])
