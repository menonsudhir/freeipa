"""
Overview:
TestSuite to verify BZs related to DNS services
SetUp Requirements:
-Latest version of RHEL OS
-Need to test for Master
-Make sure IPA server is setup with DNS
"""

import pytest
import re
from ipa_pytests.qe_install import setup_master
from ipa_pytests.qe_install import uninstall_server
from ipa_pytests.qe_install import set_hostname
from ipa_pytests.qe_install import set_etc_hosts

class TestBugCheck(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)
        print("\nChecking IPA server package whether installed on MASTER")
        output = multihost.master.run_command(['rpm', '-q', 'ipa-server'],
                                              set_env=False,
                                              raiseonerr=False)
        if output.returncode != 0:
            print("IPA server package not found on MASTER, thus installing")
            multihost.master.run_command(['yum',
                                          '-y',
                                          'install',
                                          'ipa-server*'],
                                         set_env=False,
                                         raiseonerr=False)
        else:
            print("\n IPA server package found on MASTER, running tests")

    def test_0001_ipaverify_1207539(self, multihost):
        '''IDM-IPA-TC: dns-services: Adding TLS server certificate or public key
        with the domain name for TLSA certificate association.'''
        multihost.master.kinit_as_admin()
        tlsa = "0 0 1 d2abde240d7cd3ee6b4b28c54df034b97983" \
               "a1d16e8a410e4561cb106618e971"
        multihost.master.run_command('ipa dnsrecord-add testrelm.test test1 '
                                     '--tlsa-rec=\"' + tlsa + '\"',
                                     set_env=False, raiseonerr=False)
        check1 = multihost.master.run_command(['ipa',
                                               'dnsrecord-show',
                                               'testrelm.test',
                                               'test1'],
                                              set_env=False,
                                              raiseonerr=False)
        if check1.returncode == 0:
            print("DNS record found, thus continuing")
        else:
            pytest.xfail("DNS record not found, Bug 1207539 FAILED")
        out = "D2ABDE240D7CD3EE6B4B28C54DF034B97983A" \
              "1D16E8A410E4561CB10 6618E971"
        multihost.master.qerun(['dig', 'test1.testrelm.test', 'TLSA'],
                               exp_returncode=0,
                               exp_output=out)

    def test_0002_ipaverify_1211608_and_1207541(self, multihost):
        '''IDM-IPA-TC: dns-services: Verification for bugzilla 1211608 and 1207541'''
        multihost.master.kinit_as_admin()
        cmdstr = 'ipa dnszone-mod testrelm.test ' \
                 '--update-policy \"grant * wildcard *;\"'
        multihost.master.run_command(cmdstr)
        command1 = "ipa dnszone-show testrelm.test --all"
        command2 = "| grep wildcard"
        check3 = multihost.master.run_command(command1 + command2,
                                              raiseonerr=False)
        if check3.returncode == 0:
            print("DNSZone wildcard details found, continuing tests.")
        else:
            pytest.xfail("DNSZone not found, BZ1211608 and BZ1207541 failed")
        print("Adding a non-standard record")
        filedata = 'update add test4.testrelm.test 10 ' \
                   'IN TYPE65280 \# 4 0A000001\nsend\nquit'
        multihost.master.put_file_contents("/tmp/test4.txt", filedata)
        check4 = multihost.master.run_command('nsupdate -g /tmp/test4.txt')
        if check4.returncode == 0:
            print("Nsupdate command successful, continuing tests.")
        else:
            pytest.xfail("Nsupdate not successful, bugzillas failed")
        command3 = "ipa dnsrecord-show testrelm.test test4 --all"
        command4 = "| grep unknown"
        check5 = multihost.master.run_command(command3 + command4)
        if check5.returncode == 0:
            print("DNSrecord details found, BZ1211608 and BZ1207541 PASSED")
        else:
            print("DNSrecord not found, BZ1211608 and BZ1207541 FAILED")

    def test_0003_bz1139776(self, multihost):
        """
        IDM-IPA-TC: dns-services: Verify if LDAP MODRDN rename is supported
        """
        master1 = multihost.master
        master1.kinit_as_admin()

        old_name = 'www'
        new_name = 'testwww'

        cmdstr = ["ipa", "dnsrecord-add", master1.domain.realm, old_name,
                  "--a-rec", master1.ip]
        # Add A record for www
        master1.qerun(cmdstr, exp_returncode=0)

        cmdstr = ['dig', '{}.{}'.format(old_name, master1.domain.realm)]
        master1.qerun(cmdstr, exp_returncode=0, exp_output='ANSWER: 1,')

        # Rename A record for www to testwww
        cmdstr = ['ipa', 'dnsrecord-mod', master1.domain.realm, old_name,
                  '--rename', new_name]
        master1.qerun(cmdstr, exp_returncode=0)

        cmdstr = ['dig', '{}.{}'.format(old_name, master1.domain.realm)]
        master1.qerun(cmdstr, exp_returncode=0, exp_output='ANSWER: 0,')

        cmdstr = ['dig', '{}.{}'.format(new_name, master1.domain.realm)]
        master1.qerun(cmdstr, exp_returncode=0, exp_output='ANSWER: 1,')

        cmdstr = ['ipa', 'dnsrecord-del', master1.domain.realm, new_name,
                  '--del-all']
        master1.qerun(cmdstr,
                      exp_returncode=0,
                      exp_output='Deleted record "%s"' % new_name)

    def test_0004_bz1184065(self, multihost):
        """
        IDM-IPA-TC: dns-services: Verification of bz1184065 - PTR record synchronization for A/AAAA record tuple can fail mysteriously
        """
        uninstall_server(multihost.master)
        setup_master(multihost.master, setup_reverse=False)
        multihost.master.kinit_as_admin()
        dnszone_add = ['ipa', 'dnszone-add']
        name_server = '--name-server=' + multihost.master.hostname + '.'
        zone_name = 'newzone'
        zone_name_dot = zone_name + '.'
        ns_add = dnszone_add + [name_server, zone_name]
        multihost.master.run_command(ns_add)
        print ("New zone added successfully")

        multihost.master.kinit_as_admin()
        # arecord add
        multihost.master.run_command(['ipa', 'dnsrecord-add', zone_name, 'arecord', '--a-rec=1.2.3.4'])
        # aaaa record add
        multihost.master.run_command(['ipa', 'dnsrecord-add',
                                     zone_name, 'aaaa', "--aaaa-rec=fec0:0:a10:6000:10:16ff:fe98:193"])
        # dynamic_update enable
        multihost.master.run_command(['ipa', 'dnszone-mod', zone_name_dot, '--dynamic-update=TRUE'])
        # update_policy
        multihost.master.run_command('ipa dnszone-mod ' + zone_name_dot + ' --update-policy="grant * wildcard *;"')
        # enable sync_ptr
        multihost.master.run_command(['ipa', 'dnszone-mod', zone_name_dot, '--allow-sync-ptr=TRUE'])
        # activate keytab
        multihost.master.run_command(['kinit', '-k', '-t', '/etc/krb5.keytab', 'host/' + multihost.master.hostname])
        print("Adding aaaa records to " + zone_name)
        filedata = "update add newzone 666 IN AAAA ::2\nupdate add newzone 666 IN AAAA ::23\n" \
                   "update add newzone 666 IN AAAA ::43\nsend\nquit"
        multihost.master.put_file_contents("/tmp/test_0004_bz1184065.txt", filedata)
        # perform nsupdate
        multihost.master.run_command('nsupdate -g /tmp/test_0004_bz1184065.txt')
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'dnsrecord-find', zone_name],
                               exp_returncode=0,
                               exp_output=r'(.*)AAAA record: ::2, ::23, ::43(.*)')

    def test_0005_bz1353940(self, multihost):
        """
        IDM-IPA-TC: dns-services: Verification of bz1353940 - Creation of new DNS zone without A records fails to return NS server address
        """
        master = multihost.master
        uninstall_server(master)
        domain_new = master.hostname
        realm_new = domain_new.upper()
        hostname_new = 'bz1353940.' + domain_new
        # Set new hostname
        master.put_file_contents('/etc/hostname', hostname_new)
        master.run_command(['hostnamectl'])
        # Set /etc/hosts
        etc_hosts = master.get_file_contents('/etc/hosts')
        for remove in [master.ip, master.hostname, master.external_hostname]:
            etc_hosts = re.sub(r'^.*%s.*\n' % remove, '', etc_hosts, flags=re.MULTILINE)
        etc_hosts += '\n%s %s\n' % (master.ip, hostname_new)
        master.put_file_contents('/etc/hosts', etc_hosts)
        # Install ipa server
        multihost.master.qerun(['ipa-server-install', '--setup-dns',
                                '--forwarder', master.config.dns_forwarder,
                                '--domain', domain_new,
                                '--realm', realm_new,
                                '--admin-password', master.config.admin_pw,
                                '--ds-password', master.config.dirman_pw,
                                '--allow-zone-overlap','-U'])
        master.kinit_as_admin()
        # Verify dig retruns NS record for testrelm.test
        cmd = ['ipa', 'dnszone-add', master.domain.name]
        master.qerun(cmd, exp_returncode=0)
        cmd = ['dig', '-t', 'NS', master.domain.name]
        master.qerun(cmd, exp_returncode=0, exp_output='ANSWER: 1,')
        set_hostname(master)
        etc_hosts = re.sub(r'^.*%s.*\n' % hostname_new, '', etc_hosts, flags=re.MULTILINE)
        set_etc_hosts(master)

    def class_teardown(self, multihost):
        """ Full suite teardown """
        pass
