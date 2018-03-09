"""
This is a quick test for KDCProxy
"""
import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.user_utils import add_ipa_user, del_ipa_user
from ipa_pytests.shared.utils import (service_control, start_firewalld,
                                      stop_firewalld)
from lib import (update_krbv_conf, revert_krbv_conf,
                 change_user_passwd, pwpolicy_mod)
from ipa_pytests.qe_install import set_etc_hosts, sleep
import time
twentyseconds = 20

class TestKdcproxy(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        multihost.client = multihost.clients[0]
        multihost.realm = multihost.master.domain.realm

        print("Using following hosts for KDCProxy testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("CLIENT: %s" % multihost.client.hostname)
        print("REPLICA: %s" % multihost.replica.hostname)
        print("*" * 80)

        # Common username and password for all testcases
        multihost.testuser = "mytestuser"
        multihost.password = "Secret123"
        chpass = "Passw0rd1"
        multihost.chpasswd = "%s\n%s\n%s\n" % (multihost.password,
                                               chpass,
                                               chpass)
        multihost.repasswd = "%s\n%s\n%s\n" % (chpass,
                                               multihost.password,
                                               multihost.password)
        pwpolicy_mod(multihost, '--minlife=0')
        multihost.master.kinit_as_admin()
        # 1. Add IPA user
        add_ipa_user(multihost.master, multihost.testuser, multihost.password)

    def test_0001_kdcproxy(self, multihost):
        """
        IDM-IPA-TC: KDCProxy: verify kinit, kvno success on client having KDC Proxy configured on server
        """
        # Modify client krb5.conf for KDC Proxy,
        # Run kinit / kvno / kpasswd

        # stop Firewalld on both server
        stop_firewalld(multihost.master)
        stop_firewalld(multihost.replica)

        multihost.master.kinit_as_admin()
        multihost.client.qerun(['kdestroy', '-A'], exp_returncode=0)
        # 2. Update /etc/krb5.conf with KdcProxy route
        update_krbv_conf(multihost)
        # Automation for BZ1362537
        proxy_file = '/etc/httpd/conf.d/ipa-kdc-proxy.conf'
        if not multihost.master.transport.file_exists(proxy_file):
            pytest.xfail("BZ1362537 Found")
        multihost.client.kinit_as_user(multihost.testuser, multihost.password)
        # 3. Run klist as User
        multihost.client.qerun(['klist'], exp_returncode=0)
        # 4. Run kvno as User
        multihost.client.qerun(['kvno',
                                'http/' +
                                multihost.master.hostname + "@" +
                                multihost.realm],
                               exp_returncode=0)
        # 5. Change password for user
        change_user_passwd(multihost,
                           multihost.testuser,
                           multihost.chpasswd)
        change_user_passwd(multihost,
                           multihost.testuser,
                           multihost.repasswd)

    def test_0002_kdcproxy_server_disable(self, multihost):
        """
        IDM-IPA-TC: KDCProxy: verify kinit, kvno fails when kdcproxy disabled on server
        """
        # Server disable KDC Proxy Modify client krb5.conf
        # for KDC Proxy
        # Run kinit / kvno / kpasswd

        # 0. Pre-requisite
        stop_firewalld(multihost.master)
        stop_firewalld(multihost.replica)
        # 1. Disable kdcproxy on server using ipa-ldap-updater
        multihost.master.qerun(['/usr/sbin/ipa-ldap-updater',
                                '/usr/share/ipa/kdcproxy-disable.uldif'],
                               exp_returncode=0)
        # 2. Restart httpd on server
        service_control(multihost.master, 'httpd', 'restart')
        # 3. Stop sssd on client
        service_control(multihost.client, 'sssd', 'stop')
        multihost.client.qerun(['kdestroy', '-A'], exp_returncode=0)
        # 4. Clean SSSD cache on client
        cmd = multihost.client.run_command(['/usr/sbin/sss_cache', '-E'],
                                           raiseonerr=False)
        if cmd.returncode not in [0, 2]:
            pytest.xfail("sss_cache failed with error code %d"
                         % (cmd.returncode))
        multihost.client.qerun(['rm', '-rf', '/var/lib/sss/db/*'],
                               exp_returncode=0)
        multihost.client.qerun(['rm', '-rf', '/var/lib/sss/mc/*'],
                               exp_returncode=0)
        # 5. Start SSSD on client
        service_control(multihost.client, 'sssd', 'start')
        cmd = multihost.client.run_command(['kinit', multihost.testuser],
                                           stdin_text=multihost.password,
                                           raiseonerr=False)
        if cmd.returncode != 1:
            pytest.xfail("Kinit %s successfully expecting "
                         "failure" % (multihost.testuser))
        multihost.client.qerun(['klist'],
                               exp_returncode=1)
        multihost.client.qerun(['kvno',
                                'http/' +
                                multihost.master.hostname + "@" +
                                multihost.realm],
                               exp_returncode=1)
        # 6. Change password
        change_user_passwd(multihost,
                           multihost.testuser,
                           multihost.chpasswd,
                           exp_returncode=1)
        # Clean up
        multihost.master.qerun(['/usr/sbin/ipa-ldap-updater',
                                '/usr/share/ipa/kdcproxy-enable.uldif'],
                               exp_returncode=0)
        service_control(multihost.master, 'httpd', 'restart')

    def test_0003_kdcproxy_firewall_enable(self, multihost):
        """
        IDM-IPA-TC: KDCProxy: verify kinit fails when firewalld active on server
        """
        # Server enable firewalld
        # Modify client krb5.conf for KDC Proxy
        # Run kinit / kvno / kpasswd

        # 1. Enable Firewalld
        start_firewalld(multihost.master)
        start_firewalld(multihost.replica)
        service_control(multihost.client, 'sssd', 'restart')
        multihost.client.qerun(['kdestroy', '-A'], exp_returncode=0)
        # 3. Run kinit
        cmd = multihost.client.run_command(['kinit', multihost.testuser],
                                           stdin_text=multihost.password,
                                           raiseonerr=False)
        if cmd.returncode != 1:
            pytest.xfail("Kinit %s successfully expecting "
                         "failure" % (multihost.testuser))
        # 4. Run klist
        multihost.client.qerun(['klist'],
                               exp_returncode=1)
        # 5. Run Kvno
        multihost.client.qerun(['kvno',
                                'http/' +
                                multihost.master.hostname + "@" +
                                multihost.realm],
                               exp_returncode=1)
        # 6. Run kpasswd
        multihost.client.qerun(['kpasswd', multihost.testuser],
                               exp_returncode=1)
        # Clean up
        stop_firewalld(multihost.master)
        stop_firewalld(multihost.replica)

    def test_0004_kdcproxy_multiple_replica(self, multihost):
        """
        IDM-IPA-TC: verify kinit success with multiple KDC Proxy configured
        """
        # Modify client krb5.conf with multiple kdc
        # Run kinit / kvno / kpasswd

        # 0. Pre-requisite
        stop_firewalld(multihost.master)
        stop_firewalld(multihost.replica)
        # 1. Revert client krb5
        revert_krbv_conf(multihost)
        # 2. Update krb5 with multiple replica
        update_krbv_conf(multihost, replica=True)
        multihost.client.qerun(['kdestroy', '-A'], exp_returncode=0)
        # 3. Run Kinit
        multihost.client.kinit_as_user(multihost.testuser, multihost.password)
        # 4. Run klist
        multihost.client.qerun(['klist'], exp_returncode=0)
        # 5. Run kvno
        multihost.client.qerun(['kvno',
                                'http/' +
                                multihost.master.hostname + "@" +
                                multihost.realm],
                               exp_returncode=0)
        # 6. Try to change password using kpasswd
        change_user_passwd(multihost,
                           multihost.testuser,
                           multihost.chpasswd)
        change_user_passwd(multihost,
                           multihost.testuser,
                           multihost.repasswd)

    def test_0005_kdcproxy_firewalld_multiple_replica(self, multihost):
        """
        IDM-IPA-TC: KDCProxy: verify kinit, on client success, firewall active on master, mulitple KDC Proxy configured
        """
        # Start firewalld on master,
        # Modify client krb5.conf with multiple kdc
        # Run kinit / kvno / kpasswd

        # 0. Pre-requisite
        stop_firewalld(multihost.master)
        stop_firewalld(multihost.replica)
        # 1. Revert client krb5
        revert_krbv_conf(multihost)
        # 2. Update krb5 with multiple replica
        update_krbv_conf(multihost, replica=True)
        # 3. Enable and start firewall on Master server
        set_etc_hosts(multihost.master, multihost.client)
        set_etc_hosts(multihost.replica, multihost.client)
        start_firewalld(multihost.master)
        # Sleep for 20 seconds
        sleep(twentyseconds)
        service_control(multihost.master, 'httpd', 'restart')         
        sleep(twentyseconds)
        service_control(multihost.replica, 'httpd', 'restart')
        sleep(twentyseconds)
        multihost.client.qerun(['kdestroy', '-A'], exp_returncode=0)
        # 4. Run kinit
        multihost.client.kinit_as_user(multihost.testuser, multihost.password)
        # 5. Run klist
        multihost.client.qerun(['klist'], exp_returncode=0)
        # 6. Run kvno
        multihost.client.qerun(['kvno',
                                'http/' +
                                multihost.master.hostname + "@" +
                                multihost.realm],
                               exp_returncode=0)
        # 7. Try changing password for user using kpasswd
        change_user_passwd(multihost,
                           multihost.testuser,
                           multihost.chpasswd)
        change_user_passwd(multihost,
                           multihost.testuser,
                           multihost.repasswd)
        # Cleanup
        stop_firewalld(multihost.master)

    def test_0006_kdcproxy_no_http_anchors(self, multihost):
        """
        IDM-IPA-TC: KDCProxy: verify kinit success with no http_anchors
        """
        # Modify client krb5.conf with no http_anchor
        # Run kinit/kvno/kpasswd

        # 0. Pre-requisite
        stop_firewalld(multihost.master)
        stop_firewalld(multihost.replica)
        # 1. Revert client krb5.conf
        revert_krbv_conf(multihost)
        # 2. Modify client krb5.conf for http_anchors
        update_krbv_conf(multihost)
        print("Sleeping for [{0}] seconds".format(twentyseconds))
        sleep(twentyseconds)
        multihost.client.qerun(['kdestroy', '-A'], exp_returncode=0)
        # 3. Run kinit
        multihost.client.kinit_as_user(multihost.testuser, multihost.password)
        # 4. Run klist
        multihost.client.qerun(['klist'], exp_returncode=0)
        # 5. Run kvno
        multihost.client.qerun(['kvno',
                                'http/' +
                                multihost.master.hostname + "@" +
                                multihost.realm],
                               exp_returncode=0)
        # 6. Try changing password for user using kpasswd
        change_user_passwd(multihost,
                           multihost.testuser,
                           multihost.chpasswd)
        change_user_passwd(multihost,
                           multihost.testuser,
                           multihost.repasswd)

    def test_0007_kdcproxy_no_http_anchors(self, multihost):
        """
        IDM-IPA-TC: KDCProxy: kinit fails when http_anchors removed from system restore
        """
        # Modify client krb5.conf with no http_anchors
        # And not in system store
        # Run kinit/kvno/kpasswd

        # 0. Pre-requisite
        stop_firewalld(multihost.master)
        stop_firewalld(multihost.replica)
        # 1. Revert client Krb5.conf
        revert_krbv_conf(multihost)
        # 2. Remove http_anchors from system restore
        multihost.client.qerun(['mv', '/etc/pki/ca-trust/source/ipa.p11-kit',
                                '/tmp/ipa.p11-kit'], exp_returncode=0)
        # 3. Modify client krb5.conf
        update_krbv_conf(multihost)
        # 4. Run update-ca-trust
        multihost.client.qerun(['update-ca-trust'], exp_returncode=0)
        multihost.client.qerun(['kdestroy', '-A'], exp_returncode=0)
        # 5. Run kinit
        cmd = multihost.client.run_command(['kinit', multihost.testuser],
                                           stdin_text=multihost.password,
                                           raiseonerr=False)
        if cmd.returncode != 1:
            pytest.xfail("Kinit %s successfully expecting "
                         "failure" % (multihost.testuser))
        # 6. Run klist
        multihost.client.qerun(['klist'],
                               exp_returncode=1)
        # 7. Run kvno
        multihost.client.qerun(['kvno',
                                'http/' +
                                multihost.master.hostname + "@" +
                                multihost.realm],
                               exp_returncode=1)
        # 8. Try to change password for user using kpasswd
        multihost.client.qerun(['kpasswd', multihost.testuser],
                               exp_returncode=1)

    def test_0008_kdcproxy_correct_http_anchor(self, multihost):
        """
        IDM-IPA-TC: KDCProxy: verify kinit success when http_anchor points to PEM file and trust anchor in the system store
        """
        # Modify client krb5.conf with http_anchors points
        # to PEM file, trust anchor in the system store
        # Run kinit/kvno/kpasswd

        # 0. Pre-requisite
        stop_firewalld(multihost.master)
        stop_firewalld(multihost.replica)
        # 1. Revert client krb5.conf
        revert_krbv_conf(multihost)
        # 2. Update client krb5.conf using correct PEM file
        update_krbv_conf(multihost, httpanchor='FILE:/etc/ipa/ca.crt')
        multihost.client.qerun(['kdestroy', '-A'], exp_returncode=0)
        # 3. Run kinit
        multihost.client.kinit_as_user(multihost.testuser, multihost.password)
        # 4. Run klist
        multihost.client.qerun(['klist'], exp_returncode=0)
        # 5. Run kvno
        multihost.client.qerun(['kvno',
                                'http/' +
                                multihost.master.hostname + "@" +
                                multihost.realm],
                               exp_returncode=0)
        # 6. Try to change password of user using kpasswd
        change_user_passwd(multihost,
                           multihost.testuser,
                           multihost.chpasswd)
        change_user_passwd(multihost,
                           multihost.testuser,
                           multihost.repasswd)

    def test_0009_kdcproxy_nonexistent_http_anchor(self, multihost):
        """
        IDM-IPA-TC: KDCProxy: verify kinit fails when http_anchors points to non-existent PEM with no trust anchor
        """
        # Modify client krb5.conf with http_anchors points
        # to non-existent PEM file, no trust anchor in the
        # system store
        # Run kinit/kvno/kpasswd

        # 0. Pre-requisite
        stop_firewalld(multihost.master)
        stop_firewalld(multihost.replica)
        # 1. Revert Client krb5.conf
        revert_krbv_conf(multihost)
        # 2. Modify Client krb5.conf using non-existent PEM file
        update_krbv_conf(multihost, httpanchor='FILE:/tmp/non-existent.crt')
        multihost.client.qerun(['kdestroy', '-A'], exp_returncode=0)
        # 3. Run kinit
        cmd = multihost.client.run_command(['kinit', multihost.testuser],
                                           stdin_text=multihost.password,
                                           raiseonerr=False)
        if cmd.returncode != 1:
            pytest.xfail("Kinit %s successfully expecting "
                         "failure" % (multihost.testuser))
        # 4. Run klist
        multihost.client.qerun(['klist'],
                               exp_returncode=1)
        # 5. Run kvno
        multihost.client.qerun(['kvno',
                                'http/' +
                                multihost.master.hostname + "@" +
                                multihost.realm],
                               exp_returncode=1)
        # 6. Try to change password of user using kpasswd
        multihost.client.qerun(['kpasswd', multihost.testuser],
                               exp_returncode=1)

    def test_0010_kdcproxy_incorrect_http_anchors(self, multihost):
        """
        IDM-IPA-TC: KDCProxy: verify kinit fails when http_anchors points to incorrect PEM, no trust anchor
        """
        # Modify client krb5.conf with http_anchors points
        # to incorrect PEM file, no trust anchor in the
        # system store Run
        # kinit/kvno/kpasswd

        # 0. Pre-requisite
        stop_firewalld(multihost.replica)
        stop_firewalld(multihost.master)
        # 1. Revert Client krb5.conf
        revert_krbv_conf(multihost)
        # 2. Modify Client krb5.conf using non-existent PEM file
        httpanchorfile = 'FILE:/etc/pki/tls/certs/ca-bundle.crt'
        update_krbv_conf(multihost, httpanchor=httpanchorfile)
        multihost.client.qerun(['kdestroy', '-A'], exp_returncode=0)
        # 3. Run kinit
        cmd = multihost.client.run_command(['kinit', multihost.testuser],
                                           stdin_text=multihost.password,
                                           raiseonerr=False)
        if cmd.returncode != 1:
            pytest.xfail("Kinit %s successfully expecting "
                         "failure" % (multihost.testuser))
        # 4. Run klist
        multihost.client.qerun(['klist'],
                               exp_returncode=1)
        # 5. Run kvno
        multihost.client.qerun(['kvno',
                                'http/' +
                                multihost.master.hostname + "@" +
                                multihost.realm],
                               exp_returncode=1)
        # 6. Try to change password of user using kpasswd
        multihost.client.qerun(['kpasswd', multihost.testuser],
                               exp_returncode=1)
        # Cleanup
        multihost.client.qerun(['mv', '/tmp/ipa.p11-kit',
                                '/etc/pki/ca-trust/source/ipa.p11-kit'],
                               exp_returncode=0)
        multihost.client.qerun(['update-ca-trust'], exp_returncode=0)
        service_control(multihost.client, 'sssd', 'restart')

    def test_0011_kdcproxy_firewall_enable_with_https_unblock(self, multihost):
        """
        IDM-IPA-TC: KDCProxy: verify kinit fails when firewalld active and https and http unblocked on server
        """
        # Server enable firewalld
        # with https and http unblocked
        # Modify client krb5.conf for KDC Proxy
        # Run kinit / kvno / kpasswd

        stop_firewalld(multihost.replica)
        stop_firewalld(multihost.master)
        # 1. Revert client krb5.conf
        revert_krbv_conf(multihost)
        # 2. Modify client krb5.conf
        update_krbv_conf(multihost)
        # 3. Enable Firewalld
        start_firewalld(multihost.replica)
        start_firewalld(multihost.master)
        # 4. Start Firewalld and unblock 80 and 443
        for port in ['80', '443']:
            multihost.master.qerun(['firewall-cmd', '--permanent',
                                    '--add-port=' + port + '/tcp'],
                                   exp_returncode=0)
            multihost.master.qerun(['firewall-cmd', '--reload'],
                                   exp_returncode=0)

        service_control(multihost.client, 'sssd', 'restart')
        sleep(twentyseconds)
        multihost.client.qerun(['kdestroy', '-A'], exp_returncode=0)
        # 5. Run kinit
        cmd = multihost.client.run_command(['kinit', multihost.testuser],
                                           stdin_text=multihost.password,
                                           raiseonerr=False)
        if cmd.returncode != 0:
            pytest.xfail("Kinit %s failed expecting "
                         "success" % (multihost.testuser))
        # 6. Run klist
        multihost.client.qerun(['klist'], exp_returncode=0)
        # 7. Run Kvno
        multihost.client.qerun(['kvno',
                                'http/' +
                                multihost.master.hostname + "@" +
                                multihost.realm],
                               exp_returncode=0)

        # 8. Try changing password for user using kpasswd
        change_user_passwd(multihost,
                           multihost.testuser,
                           multihost.chpasswd)
        change_user_passwd(multihost,
                           multihost.testuser,
                           multihost.repasswd)
        # 9. Clean up
        for port in ['80', '443']:
            multihost.master.qerun(['firewall-cmd', '--permanent',
                                    '--remove-port=' + port + '/tcp'],
                                   exp_returncode=0)
            multihost.master.qerun(['firewall-cmd', '--reload'],
                                   exp_returncode=0)
        stop_firewalld(multihost.master)
        stop_firewalld(multihost.replica)

    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Class teardown for KDCProxy")
        pwpolicy_mod(multihost, '--minlife=20')
        del_ipa_user(multihost.master, multihost.testuser)
        cfg = '/etc/krb5.conf'
        multihost.client.qerun(['mv', cfg + ".bak", cfg], exp_returncode=0)
