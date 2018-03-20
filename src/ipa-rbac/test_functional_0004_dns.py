"""
Overview:
Test suite cover the functional tests of Role Based Access Control
which has 3 sets of clis: privilege, privilege and role
"""

from __future__ import print_function
import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.user_utils import add_ipa_user, del_ipa_user
from ipa_pytests.shared.role_utils import role_add_member, role_add_privilege, role_add
from ipa_pytests.shared.role_utils import role_del
from ipa_pytests.shared.paths import IPA
from ipa_pytests.shared.privilege_utils import privilege_add, privilege_add_permission
from ipa_pytests.shared.privilege_utils import privilege_del


class TestFunctionalDNS(object):
    """
    Test to verify bz801931 - Per-domain DNS record permissions
    """
    login4 = "dnsuser1"
    password4 = "Secret123"
    ipaddr = ""
    zone1 = ""
    zone2 = ""
    dns_priv = "DNSTestPrivilege"
    dns_role = "DNSTestRole"
    email = "ipaqa_redhat@test.com"

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_setup(self, multihost):
        """
        Setup common to all functions
        :param multihost:
        :return:
        """
        multihost.master.kinit_as_admin()
        self.ipaddr = multihost.master.hostname
        self.zone1 = "one." + multihost.master.domain.name
        self.zone2 = "two." + multihost.master.domain.name
        add_ipa_user(multihost.master,
                     self.login4,
                     self.password4,
                     "dnsuser1fisrt",
                     "dnsuser1last")
        multihost.master.run_command([IPA, 'dnszone-add', self.zone1,
                                      '--name-server=' + self.ipaddr + '.',
                                      '--admin-email=' + self.email])
        multihost.master.run_command([IPA, 'dnszone-add', self.zone2,
                                      '--name-server=' + self.ipaddr + '.',
                                      '--admin-email=' + self.email])
        privilege_add(multihost.master,
                      self.dns_priv,
                      ['--desc=' + self.dns_priv])
        role_add(multihost.master,
                 self.dns_role,
                 ['--desc=' + self.dns_role])
        role_add_privilege(multihost.master,
                           self.dns_role,
                           ['--privileges=' + self.dns_priv])
        multihost.master.run_command([IPA,
                                      'dnszone-add-permission',
                                      self.zone1])
        privilege_add_permission(multihost.master,
                                 self.dns_priv,
                                 ['--permission=Manage DNS zone ' + self.zone1+"."])
        role_add_member(multihost.master,
                        self.dns_role,
                        ['--users=' + self.login4, '--all'])
        multihost.master.kinit_as_user(self.login4, self.password4)

    def test0001(self, multihost):
        """IDM-IPA-TC : rbac : Can list zone managed by user"""
        multihost.master.kinit_as_user(self.login4, self.password4)
        check4_1 = multihost.master.run_command([IPA, 'dnszone-show',
                                                 "one." + multihost.master.domain.name,
                                                 '--all'])
        if check4_1.returncode:
            pytest.fail(check4_1.stderr_text)
        else:
            print ("dnszone-show  lists the zone managed by user")
            print (check4_1.stdout_text)

    def test0002(self, multihost):
        """IDM-IPA-TC : rbac : Cannot list zone not managed by user"""
        check4_2 = multihost.master.run_command([IPA, 'dnszone-show',
                                                 "two."+multihost.master.domain.name,
                                                 '--all'],
                                                raiseonerr=False)
        exp_output4_2 = "ipa: ERROR: two."+multihost.master.domain.name +\
                        ".: DNS zone not found"
        if exp_output4_2 in check4_2.stderr_text:
            print ("no DNS zone is shown as expected")
        else:
            pytest.fail(check4_2.stderr_text)

    def test0003(self, multihost):
        """IDM-IPA-TC : rbac : Cannot add permission for zone not managed by user"""
        check4_3 = multihost.master.run_command([IPA, 'dnszone-add-permission',
                                                 'two.'+multihost.master.domain.name],
                                                raiseonerr=False)
        exp_output4_3 = "ipa: ERROR: two."+multihost.master.domain.name +\
                        ".: DNS zone not found"
        if exp_output4_3 in check4_3.stderr_text:
            print('two.'+multihost.master.domain.name + " adding failed as expected")
        else:
            pytest.fail(check4_3.stderr_text)

    def test0004(self, multihost):
        """IDM-IPA-TC : rbac : Cannot add a new zone"""
        test_zone = "testzone." + multihost.master.domain.name
        check4_4 = multihost.master.run_command([IPA, 'dnszone-add', test_zone,
                                                 '--name-server='+multihost.master.hostname+'.',
                                                 '--admin-email=' + self.email],
                                                raiseonerr=False)
        exp_output4_4 = "ipa: ERROR: Insufficient access: Insufficient 'add' privilege"
        if exp_output4_4 in check4_4.stderr_text:
            print("adding of " + test_zone + " failed as expected")
        else:
            pytest.fail(check4_4.stderr_text)

    def test0005(self, multihost):
        """IDM-IPA-TC : rbac : Cannot delete zone managed by user"""
        check4_5 = multihost.master.run_command([IPA, 'dnszone-del',
                                                 'one.'+multihost.master.domain.name],
                                                raiseonerr=False)
        exp_output4_5 = "ipa: ERROR: Insufficient access: Insufficient 'delete' privilege " \
                        "to delete the entry 'idnsname=one."+multihost.master.domain.name + \
                        ".,cn=dns," + multihost.master.domain.basedn.replace('"', '') + "'."
        if exp_output4_5 in check4_5.stderr_text:
            print("deleting of zone1 failed as expected")
        else:
            pytest.fail(check4_5.stderr_text)

    def test0006(self, multihost):
        """IDM-IPA-TC : rbac : Cannot edit managedBy attr for zone managed by user"""
        c = multihost.master.run_command([IPA, 'dnszone-mod',
                                          'one.'+multihost.master.domain.name,
                                          '--setattr=managedBy=uid=dnsuser2,cn=users,cn=accounts,'
                                          + multihost.master.domain.basedn.replace('"', '')],
                                         raiseonerr=False)
        if c.returncode:
            print("editing ManageBy attr failed as expected")
        else:
            pytest.fail(c.stdout_text)

    def test0007(self, multihost):
        """IDM-IPA-TC : rbac : Can enable and disable zone managed by user"""
        check4_7 = multihost.master.run_command([IPA, 'dnszone-disable',
                                                 'one.'+multihost.master.domain.name])
        check4_7a = multihost.master.run_command([IPA, 'dnszone-enable',
                                                  'one.'+multihost.master.domain.name])
        if check4_7.returncode == 0 and check4_7a.returncode == 0:
            print("enabling and disabling zone managed by user succeeded")
        else:
            pytest.fail(check4_7.stderr_text+"\n"+check4_7a.stderr_text)

    def test0008(self, multihost):
        """IDM-IPA-TC : rbac : Cannot enable and disable zone not managed by user"""
        check4_8 = multihost.master.run_command([IPA, 'dnszone-disable',
                                                 'two.'+multihost.master.domain.name],
                                                raiseonerr=False)
        exp_output4_8 = "ipa: ERROR: two."+multihost.master.domain.name \
                        + ".: DNS zone not found"
        if exp_output4_8 in check4_8.stderr_text:
            print("disabling zone not managed by user failed ad expected")
        else:
            pytest.xfail(check4_8.stderr_text)
        check4_8a = multihost.master.run_command([IPA, 'dnszone-enable',
                                                  'two.'+multihost.master.domain.name],
                                                 raiseonerr=False)
        exp_output4_8a = "ipa: ERROR: two."+multihost.master.domain.name + \
                         ".: DNS zone not found"
        if exp_output4_8a in check4_8a.stderr_text:
            print("enabling zone not managed by user failed ad expected")
        else:
            pytest.fail(check4_8a.stderr_text)

    def test0009(self, multihost):
        """IDM-IPA-TC : rbac : Can read Global configuration but cannot modify it"""
        multihost.master.run_command([IPA, 'dnsconfig-show'])
        check4_9a = multihost.master.run_command([IPA, 'dnsconfig-mod',
                                                  '--allow-sync-ptr=TRUE'], raiseonerr=False)
        exp_output4_9a = "ipa: ERROR: Insufficient access: Insufficient 'write' privilege " \
                         "to the 'idnsAllowSyncPTR' attribute of entry 'cn=dns," + \
                         multihost.master.domain.basedn.replace('"', '') + "'."
        if exp_output4_9a in check4_9a.stderr_text:
            print("modifying global configuration failed as expected")
        else:
            pytest.fail(check4_9a.stderr_text)
        check4_9b = multihost.master.run_command([IPA, 'dnsconfig-mod',
                                                  '--forwarder=1.1.1.1'], raiseonerr=False)
        exp_output4_9b = "ipa: ERROR: Insufficient access: Insufficient 'write' privilege " \
                         "to the 'idnsForwarders' attribute of entry 'cn=dns," + \
                         multihost.master.domain.basedn.replace('"', '') + "'."
        if exp_output4_9b in check4_9b.stderr_text:
            print("modifying global configuration failed as expected")
        else:
            pytest.fail(check4_9b.stderr_text)

    def test00010(self, multihost):
        """IDM-IPA-TC : rbac : Can add delete modify find DNS records"""
        arecord_name = "ARecord"
        arecord = "--a-rec=1.1.1.1 --a-rec=2.2.2.2"
        arecord_ip2 = "2.2.2.2"
        txtrecord = "ABC"
        self.zone1 = 'one.'+multihost.master.domain.name+"."
        multihost.master.kinit_as_user(self.login4, self.password4)
        multihost.master.run_command("ipa dnsrecord-add "+self.zone1+" "+arecord_name+" " +
                                     arecord)
        check4_10a = multihost.master.run_command([IPA,
                                                   'dnsrecord-show',
                                                   self.zone1,
                                                   arecord_name],
                                                  raiseonerr=False)
        if arecord_ip2 not in check4_10a.stdout_text:
            pytest.fail(check4_10a.stderr_text)
        multihost.master.run_command([IPA,
                                      'dnsrecord-mod',
                                      self.zone1,
                                      arecord_name,
                                      '--txt-rec',
                                      txtrecord],
                                     raiseonerr=False)
        check4_10b = multihost.master.run_command([IPA,
                                                   'dnsrecord-find',
                                                   self.zone1,
                                                   arecord_name],
                                                  raiseonerr=False)
        if txtrecord not in check4_10b.stdout_text:
            pytest.fail(check4_10b.stderr_text)
        multihost.master.run_command([IPA,
                                      'dnsrecord-del',
                                      self.zone1,
                                      arecord_name,
                                      '--a-rec',
                                      arecord_ip2],
                                     raiseonerr=False)
        multihost.master.run_command([IPA,
                                      'dnsrecord-del',
                                      self.zone1,
                                      '--txt-rec',
                                      txtrecord],
                                     raiseonerr=False)
        check4_10c = multihost.master.run_command([IPA,
                                                   'dnsrecord-show',
                                                   self.zone1,
                                                   arecord_name],
                                                  raiseonerr=False)
        if arecord_ip2 in check4_10c.stdout_text:
            pytest.xfail(check4_10c.stderr_text)
        check4_10d = multihost.master.run_command([IPA,
                                                   'dnsrecord-show',
                                                   self.zone1,
                                                   arecord_name],
                                                  raiseonerr=False)
        if txtrecord not in check4_10d.stdout_text:
            pytest.xfail(check4_10d.stderr_text)

    def test00011(self, multihost):
        """IDM-IPA-TC : rbac : Cannot remove permission to manage this zone"""
        check4_11 = multihost.master.run_command([IPA,
                                                  'dnszone-remove-permission',
                                                  'one.'+multihost.master.domain.name],
                                                 raiseonerr=False)
        exp_output4_11 = "ipa: ERROR: Insufficient access: Insufficient 'write' privilege " \
                         "to the 'managedBy' attribute of entry 'idnsname=one." +\
                         multihost.master.domain.name+".,cn=dns," + \
                         multihost.master.domain.basedn.replace('"', '') + "'."
        if exp_output4_11 in check4_11.stderr_text:
            print("Removing permission to manage one."+multihost.master.domain.name +
                  " failed as expected")
        else:
            pytest.fail(check4_11.stderr_text)

    def test00012(self, multihost):
        """IDM-IPA-TC : rbac : Verify can use dig to do DNS queries"""
        # add a host with an ip
        multihost.master.kinit_as_admin()
        host1 = "hostfordnstest." + 'two.'+multihost.master.domain.name
        rsplit = multihost.master.ip.split('.')
        rzone = rsplit[2] + '.' + rsplit[1] + '.' + rsplit[0] + '.in-addr.arpa.'
        hostipaddr = ""
        if rzone:
            noct = rzone.split(".")
            hostipaddr = noct[0] + "." + noct[1] + "." + noct[2] + ".99"
            multihost.master.run_command([IPA, 'host-add', host1,
                                          '--ip-address=' + hostipaddr], raiseonerr=False)
        else:
            pytest.fail("Reverse DNS zone not found.")
        multihost.master.kinit_as_user(self.login4, self.password4)
        # use dig to lookup host added
        check4_12 = multihost.master.run_command(['dig', host1], raiseonerr=False)
        if hostipaddr not in check4_12.stdout_text:
            pytest.fail(check4_12.stdout_text)
        multihost.master.kinit_as_admin()
        multihost.master.run_command([IPA, 'host-del', host1, '--updatedns'])
        multihost.master.kinit_as_user(self.login4, self.password4)

    def test00013(self, multihost):
        """IDM-IPA-TC : rbac : User with permission removed can no longer access the zone"""
        multihost.master.kinit_as_admin()
        self.zone1 = 'one.'+multihost.master.domain.name+"."
        multihost.master.run_command([IPA, 'dnszone-remove-permission', self.zone1])
        multihost.master.kinit_as_user(self.login4, self.password4)
        check4_13a = multihost.master.run_command([IPA, 'dnszone-show', self.zone1],
                                                  raiseonerr=False)
        exp_output4_13a = "ipa: ERROR: one."+multihost.master.domain.name +\
                          ".: DNS zone not found"
        if exp_output4_13a in check4_13a.stderr_text:
            print("Success! User with permission removed can no longer access the zone")
        else:
            pytest.fail(check4_13a.stderr_text)

    def test_cleanup(self, multihost):
        """
        Clean up all the test privileges, permissions and roles added
        :param multihost:
        :return:
        """
        multihost.master.kinit_as_admin()
        del_ipa_user(multihost.master, self.login4)
        multihost.master.run_command([IPA,
                                      'dnszone-del',
                                      'one.testrelm.test',
                                      'two.testrelm.test'])
        role_del(multihost.master, self.dns_role)
        privilege_del(multihost.master, self.dns_priv)
