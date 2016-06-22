"""
Overview:
TestSuite to verify BZs related to DNS services
SetUp Requirements:
-Latest version of RHEL OS
-Need to test for Master
-Make sure IPA server is setup with DNS
"""

import pytest


class Testmaster(object):
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
        '''Adding TLS server certificate or public key
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
        ''' Verification for bugzilla 1211608 and 1207541'''
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
        Verify if LDAP MODRDN rename is supported
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

    def class_teardown(self, multihost):
        """ Full suite teardown """
        pass
