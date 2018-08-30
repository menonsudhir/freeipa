"""
user tests scenarios
"""

import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.user_utils import add_ipa_user, del_ipa_user, find_ipa_user
from ipa_pytests.shared.utils import ldapmodify_cmd


class Testipauserfind(object):

    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print ("\nClass Setup")
        print ("MASTER: ", multihost.master.hostname)
        print ("CLIENT: ", multihost.client.hostname)

    #def test_0001_ipauserfinderror(self, multihost):
    #    """
    #    IDM-IPA-TC: ipa user-find: ipa user-find gives
    #                error when run on RHEL7.1 IPA client
    #    """
    #    realm = multihost.master.domain.realm
    #    multihost.client.kinit_as_admin()
    #    multihost.client.qerun(['ipa', 'user-find'], exp_returncode=1,
    #                           exp_output="ipa: ERROR:")

    #def test_0002_ipauserskipversioncheck(self, multihost):
    #    """
    #    Test to verify Bugzilla 1211589 - [RFE] Add option to skip
    #    the verify_client_version
    #    IDM-IPA-TC: ipa user-find: ipa -e skip_version_check=1
    #                user-find works without any error on RHEL7.1 client
    #    """
    #    realm = multihost.master.domain.realm
    #    multihost.client.kinit_as_admin()
    #   multihost.client.qerun(['ipa', '-e', 'skip_version_check=1',
    #                           'user-find'], exp_returncode=0,
    #                          exp_output="1 user matched")

    def test_0003_bz1288967(self, multihost):
        """
        Test to verify Bugzilla 1288967 - Normalize Manager entry in ipa
        user-add
        """
        multihost.master.kinit_as_admin()
        testuser1 = 'testuser_1288967'
        testuser2 = 'testmgr_1288967'
        opt = {'manager': testuser2}
        add_ipa_user(multihost.master, testuser2)
        add_ipa_user(multihost.master, testuser1, options=opt)
        # Manager info is shown in '--all' of user-find command
        opt['all'] = ''
        cmd = find_ipa_user(multihost.master, options=opt)
        if cmd.returncode == 0:
            if 'Manager: ' + testuser2 in cmd.stdout_text:
                del_ipa_user(multihost.master, testuser1)
                del_ipa_user(multihost.master, testuser2)
                print("BZ1288967 verified")
            else:
                del_ipa_user(multihost.master, testuser1)
                del_ipa_user(multihost.master, testuser2)
                pytest.fail("BZ1288967 failed to verify")
        else:
            del_ipa_user(multihost.master, testuser1)
            del_ipa_user(multihost.master, testuser2)
            pytest.fail("Failed to run user-find command")

    def test_0004_bz1250110(self, multihost):
        """
        @Title: IDM-IPA-TC: ldap user search with denied object in filter
        """
        user1 = 'testuser1'
        user2 = 'testuser2'
        searchdn = 'cn=users,cn=accounts,' + multihost.master.domain.basedn.replace('"', '')
        user1uid = 'uid=' + user1 + ',' + searchdn
        userpass = 'TestP@ss123'
        ldapadmin = 'cn=Directory Manager'
        adminpass = multihost.master.config.dirman_pw
        uri = 'ldap://' + multihost.master.hostname + ':389'
        add_ipa_user(multihost.master, user1, userpass)
        add_ipa_user(multihost.master, user2, userpass)
        multihost.master.qerun(['ipa', 'user-mod', user2,
                                '--phone=000-000-0000'])
        ldif = 'dn: %s\n' \
               'changetype: modify\n' \
               'add: aci\n' \
               'aci: (targetattr = "telephoneNumber")' \
               '(version 3.0;acl "Deny TelephoneNumber";deny (read)' \
               '(userdn = "ldap:///%s");)' % (searchdn, user1uid)
        ldif_file = '/tmp/bz1250110.ldif'
        multihost.master.put_file_contents(ldif_file, ldif)
        ldapmodify_cmd(multihost.master, uri, ldapadmin, adminpass, ldif_file)
        search_filter = '(|(cn=%s*)(telephonenumber=0*))' % user2
        search = ['ldapsearch', '-x', '-D', user1uid, '-w', userpass,
                  '-b', searchdn, search_filter, 'dn', 'cn', 'telephone']
        exp_output = 'uid=%s' % user2
        multihost.master.qerun(search, exp_output=exp_output)

        del_ipa_user(multihost.master, user1)
        del_ipa_user(multihost.master, user2)
        ldif = 'dn: %s\n' \
               'changetype: modify\n' \
               'delete: aci\n' \
               'aci: (targetattr = "telephoneNumber")' \
               '(version 3.0;acl "Deny TelephoneNumber";deny (read)' \
               '(userdn = "ldap:///%s");)' % (searchdn, user1uid)
        ldif_file = '/tmp/bz1250110-del.ldif'
        multihost.master.put_file_contents(ldif_file, ldif)
        ldapmodify_cmd(multihost.master, uri, ldapadmin, adminpass, ldif_file)

    def class_teardown(self, multihost):
        """ Class Teardown """
        pass
