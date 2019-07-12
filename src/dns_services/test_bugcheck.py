"""
Overview:
TestSuite to verify BZs related to DNS services
SetUp Requirements:
-Latest version of RHEL OS
-Need to test for Master
-Make sure IPA server is setup with DNS
"""

import pytest
from ipa_pytests.qe_install import setup_master
from ipa_pytests.qe_install import uninstall_server


class TestBugCheck(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_ipaverify_1207539(self, multihost):
        '''IDM-IPA-TC: dns-services: Adding TLS server certificate or public key
        with the domain name for TLSA certificate association.'''
        master = multihost.master
        master.kinit_as_admin()
        tlsa = "0 0 1 d2abde240d7cd3ee6b4b28c54df034b97983" \
               "a1d16e8a410e4561cb106618e971"

        multihost.master.run_command('ipa dnsrecord-add {0} test1 --tlsa-rec="{1}"'
                                     .format(master.domain.name, tlsa))
        rec_show = 'ipa dnsrecord-show {} test1'.format(master.domain.name)
        check1 = master.run_command(rec_show)
        if check1.returncode == 0:
            print("DNS record found, thus continuing")
        else:
            pytest.xfail("DNS record not found, Bug 1207539 FAILED")
        out = "D2ABDE240D7CD3EE6B4B28C54DF034B97983A" \
              "1D16E8A410E4561CB10 6618E971"
        dig_cmd = 'dig test1.{0} TLSA'.format(master.domain.name)
        multihost.master.qerun(dig_cmd, exp_returncode=0, exp_output=out)

    def test_0002_ipaverify_1211608_and_1207541(self, multihost):
        '''IDM-IPA-TC: dns-services: Verification for bugzilla 1211608 and 1207541'''
        master = multihost.master
        master.kinit_as_admin()

        policy = "--update-policy='grant * wildcard *;'"
        cmdstr = 'ipa dnszone-mod {0} {1}' .format(master.domain.name, policy)
        master.run_command(cmdstr)
        command1 = "ipa dnszone-show {} --all".format(master.domain.name)
        check3 = master.run_command(command1)
        assert "wildcard" in check3.stdout_text

        if check3.returncode == 0:
            print("DNSZone wildcard details found, continuing tests.")
        else:
            pytest.xfail("DNSZone not found, BZ1211608 and BZ1207541 failed")
        print("Adding a non-standard record")
        filedata = "update add test4.{} 10 IN TYPE65280 \# 4 0A000001 \nsend\nquit"\
            .format(master.domain.name)
        master.put_file_contents("/tmp/test4.txt", filedata)
        check4 = master.run_command('nsupdate -g /tmp/test4.txt')

        if check4.returncode == 0:
            print("Nsupdate command successful, continuing tests.")
        else:
            pytest.xfail("Nsupdate not successful, bugzillas failed")
        command3 = "ipa dnsrecord-show {} test4 --all".format(master.domain.name)
        check5 = master.run_command(command3)
        # check for verification of BZ1211608 and BZ1207541
        assert "unknown" in check5.stdout_text

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
        IDM-IPA-TC: dns-services: Verification of bz1184065 - PTR record
        synchronization for A/AAAA record tuple can fail mysteriously
        """
        master = multihost.master
        uninstall_server(multihost.master)
        setup_master(multihost.master, setup_reverse=False)
        master.kinit_as_admin()
        dnszone_add = ['ipa', 'dnszone-add']
        name_server = '--name-server=' + master.hostname + '.'
        zone_name = 'newzone'
        zone_name_dot = zone_name + '.'
        ns_add = dnszone_add + [name_server, zone_name]
        master.run_command(ns_add)
        print("New zone added successfully")

        master.kinit_as_admin()
        # arecord add
        master.run_command(['ipa', 'dnsrecord-add', zone_name,
                            'arecord', '--a-rec=1.2.3.4'])
        # aaaa record add
        master.run_command(['ipa', 'dnsrecord-add',
                            zone_name, 'aaaa',
                            "--aaaa-rec=fec0:0:a10:6000:10:16ff:fe98:193"])
        # dynamic_update enable
        master.run_command(['ipa', 'dnszone-mod', zone_name_dot,
                            '--dynamic-update=TRUE'])
        # update_policy

        policy = "--update-policy='grant * wildcard *;'"
        cmdstr = 'ipa dnszone-mod {0} {1}' .format(zone_name_dot, policy)
        master.run_command(cmdstr)
        # enable sync_ptr
        master.run_command(['ipa', 'dnszone-mod', zone_name_dot, '--allow-sync-ptr=TRUE'])
        # activate keytab
        master.run_command(['kinit', '-k', '-t', '/etc/krb5.keytab', 'host/' + master.hostname])
        print("Adding aaaa records to " + zone_name)
        filedata = "update add newzone 666 IN AAAA ::2\nupdate add newzone 666 IN AAAA ::23\n" \
                   "update add newzone 666 IN AAAA ::43\nsend\nquit"
        master.put_file_contents("/tmp/test_0004_bz1184065.txt", filedata)
        # perform nsupdate
        master.run_command('nsupdate -g /tmp/test_0004_bz1184065.txt')
        master.kinit_as_admin()
        master.qerun(['ipa', 'dnsrecord-find', zone_name],
                     exp_returncode=0,
                     exp_output=r'(.*)AAAA record: ::2, ::23, ::43(.*)')

    def class_teardown(self, multihost):
        """ Full suite teardown """
        pass
