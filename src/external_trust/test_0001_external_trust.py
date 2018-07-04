"""
This covers the test cases for external trust feature
"""

import pytest
from ipa_pytests.shared.utils import (disable_dnssec, dnsforwardzone_add,
                                      add_dnsforwarder, sssd_cache_reset)
from ipa_pytests.qe_install import adtrust_install
from lib import (add_external_trust, ad_domain)
import time
from ipa_pytests.shared.ssh_onclient import ssh_from_client
from ipa_pytests.shared.trust_utils import (ipa_trust_show, ipa_trust_add)
from  ipa_pytests.shared.user_utils import (id_user, getent)
from ipa_pytests.shared import paths

USER1 = 'etuser1'
USER2 = 'etuser2'
GROUP1 = 'etgsgrp'
GROUP2 = 'etgsgrp2'
GROUP3 = 'etlsgrp'
GROUP4 = 'etldgrp'
GROUP5 = 'etgdgrp'
GROUP6 = 'etusgrp'
GROUP7 = 'etudgrp'


class TestExternalTrust(object):
    """
    This covers the test cases for RFE Bugzilla 1314786
    """

    def class_setup(self, multihost):
        """ Setup for class """
        print "\nClass Setup"
        print "MASTER: ", multihost.master.hostname
        print "CLIENT: ", multihost.client.hostname
        disable_dnssec(multihost.master)

        adtrust_install(multihost.master)

        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])
        domain = multihost.master.domain.name

        etchosts = paths.ETCHOSTS
        etchostscfg = multihost.master.get_file_contents(etchosts)
        etchostscfg += '\n' + ad1.ip + ' ' + ad1.hostname + '\n'
        multihost.master.put_file_contents(etchosts, etchostscfg)

        multihost.master.run_command(['kdestroy', '-A'])
        multihost.master.kinit_as_admin()
        dnsforwardzone_add(multihost.master, forwardzone, ad1.ip)

        add_dnsforwarder(ad1, domain, multihost.master.ip)

        cmd = multihost.master.run_command(paths.DIG + ' +short SRV _ldap._tcp.' + forwardzone, raiseonerr=False)
        print cmd.stdout_text, cmd.stderr_text
        if ad1.hostname in cmd.stdout_text:
            print "dns resolution passed for ad domain"
        else:
            pytest.fail("dns resolution failed for ad domain", pytrace=False)
        cmd = multihost.master.run_command(paths.DIG + ' +short SRV @' + ad1.ip + ' _ldap._tcp.' + domain,
                                           raiseonerr=False)
        print cmd.stdout_text, cmd.stderr_text
        if domain in cmd.stdout_text:
            print "dns resolution passed for ipa domain"
        else:
            pytest.xfail("dns resolution failed for ipa domain")

    def test_0001_external_trust_with_false_option(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
         Check external trust with false option
        """
        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])

        # trust-add
        opt_list = ['--type=ad', '--external=False']
        passwd = ad1.ssh_password
        cmd = ipa_trust_add(multihost.master, forwardzone, ad1.ssh_username, opt_list, passwd)
        print "ipa trust-add\n", cmd.stdout_text

        # verifying trust add output
        if "Trust type: Active Directory domain" in cmd.stdout_text:
            print "Expected Result:\n External trust " \
                  "is not added as expected\n"
        else:
            pytest.xfail("Test failed: external trust with false option ")

    def test_0002_verifying_external_trust_users(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check external trust users are resolved
        """
        addomain = ad_domain(multihost)

        # adding external trust
        add_external_trust(multihost)

        # verifying user
        #id_user(multihost.master, USER1 + '@' + addomain)

        # cleaning sssd cache
        sssd_cache_reset(multihost.master)
        print "waiting for 60 seconds"
        time.sleep(60)

        # verifying user
        id_user(multihost.master, USER1 + '@' + addomain)
        # getent passwd
        getent(multihost.master, 'passwd', USER1 + '@' + addomain, exp_output=USER1)

    def test_0003_verifying_global_security_group(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check external trust global security group is resolved
        """
        addomain = ad_domain(multihost)

        # adding external trust
        add_external_trust(multihost)

        # cleaning sssd cache
        sssd_cache_reset(multihost.master)
        print "waiting for 60 seconds"
        time.sleep(60)

        # getent group
        getent(multihost.master, 'group', GROUP1 + '@' + addomain, exp_output=GROUP1)

    def test_0004_verifying_users_under_global_security_group(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check external trust users under group is resolved
        """
        addomain = ad_domain(multihost)

        # adding external trust
        add_external_trust(multihost)

        # cleaning sssd cache
        sssd_cache_reset(multihost.master)
        print "waiting for 60 seconds"
        time.sleep(60)

        # getent group
        getent(multihost.master, 'group', GROUP2 + '@' + addomain, exp_output=USER2)

    def test_0005_verifying_local_security_group(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check external trust domain local security group is resolved
        """
        addomain = ad_domain(multihost)

        # adding external trust
        add_external_trust(multihost)

        # cleaning sssd cache
        sssd_cache_reset(multihost.master)
        print "waiting for 60 seconds"
        time.sleep(60)

        # getent group
        getent(multihost.master, 'group', GROUP3 + '@' + addomain, exp_returncode=2)

    def test_0006_verifying_local_distribution_group(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check domain local distribution group is resolved
        """
        addomain = ad_domain(multihost)

        # adding external trust
        add_external_trust(multihost)

        # cleaning sssd cache
        sssd_cache_reset(multihost.master)
        print "waiting for 60 seconds"
        time.sleep(60)

        # getent group
        getent(multihost.master, 'group', GROUP4 + '@' + addomain, exp_returncode=2)

    def test_0007_verifying_global_distribution_group(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check domain global distribution group is resolved
        """
        addomain = ad_domain(multihost)

        # adding external trust
        add_external_trust(multihost)

        # cleaning sssd cache
        sssd_cache_reset(multihost.master)
        print "waiting for 60 seconds"
        time.sleep(60)

        # getent group
        getent(multihost.master, 'group', GROUP5 + '@' + addomain, exp_returncode=2)

    def test_0008_verifying_universal_security_group(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
         Check domain universal security group is resolved
        """
        addomain = ad_domain(multihost)

        # adding external trust
        add_external_trust(multihost)

        # cleaning sssd cache
        sssd_cache_reset(multihost.master)
        print "waiting for 60 seconds"
        time.sleep(60)

        # getent group
        getent(multihost.master, 'group', GROUP6 + '@' + addomain, exp_output=GROUP6)

    def test_0009_verifying_universal_distribution_group(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check domain universal distribution group is resolved
        """
        addomain = ad_domain(multihost)

        # adding external trust
        add_external_trust(multihost)

        # cleaning sssd cache
        sssd_cache_reset(multihost.master)
        print "waiting for 60 seconds"
        time.sleep(60)

        # getent group
        getent(multihost.master, 'group', GROUP7 + '@' + addomain, exp_returncode=2)

    def test_0010_verifying_trust_show_command(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check trust show displays external trust as nontransitive
        """
        addomain = ad_domain(multihost)

        # adding external trust
        add_external_trust(multihost)

        # ipa trust-show
        cmd = ipa_trust_show(multihost.master, addomain)
        print "ipa trust-show\n", cmd.stdout_text

        multihost.expectresult = "Trust type: Non-transitive external" \
                                 " trust to a domain in another" \
                                 " Active Directory forest"

        if multihost.expectresult in cmd.stdout_text:
            print "Trust show works as expected\n"
        else:
            pytest.fail("Trust show fails", pytrace=False)

    def test_0011_verifying_trust_show_with_all_option(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check trust show with all options displays all attributes
        """
        addomain = ad_domain(multihost)

        # adding external trust
        add_external_trust(multihost)

        # ipa trust-show
        opt_list = ['--all']
        cmd = ipa_trust_show(multihost.master, addomain, opt_list)
        print "ipa trust-show --all\n", cmd.stdout_text

        # verifying trust show output
        if all(x in cmd.stdout_text for x in ["SID blacklist incoming",
                                              "SID blacklist outgoing",
                                              "ipantsupportedencryptiontypes",
                                              "ipantsecurityidentifier",
                                              "ipanttrustauthincoming",
                                              "ipanttrustpartner",
                                              "ipanttrustposixoffset",
                                              "objectclass"]):
            print "Trust show with --all option works as expected\n"
        else:
            pytest.fail("Trust show --all fails", pytrace=False)

    def test_0012_verifying_trust_show_with_all_rights_option(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check trust show with all right options displays attributes
        """
        addomain = ad_domain(multihost)

        # adding external trust
        add_external_trust(multihost)

        # ipa trust-show
        opt_list = ['--all', '--rights']
        cmd = ipa_trust_show(multihost.master, addomain, opt_list)
        print "ipa trust-show --all --rights\n", cmd.stdout_text

        # verifying trust show output
        if "attributelevelrights" in cmd.stdout_text:
            print "Trust show with --all --rights option works as expected\n"
        else:
            pytest.fail("Trust show --all --rights fails", pytrace=False)

    def test_0013_verifying_trust_show_with_raw_option(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check trust show with raw options displays information
        """
        addomain = ad_domain(multihost)

        # adding external trust
        add_external_trust(multihost)

        # ipa trust-show
        opt_list = ['--raw']
        cmd = ipa_trust_show(multihost.master, addomain, opt_list)
        print "ipa trust-show --raw\n", cmd.stdout_text

        # verifying trust show output
        if all(x in cmd.stdout_text for x in ["ipanttrusteddomainsid",
                                              "ipantflatname", "cn"]):
            print "Trust show with --raw option" \
                  " works as expected\n"
        else:
            pytest.fail("Trust show --raw fails", pytrace=False)

    def test_0014_verifying_trust_show_with_all_option(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check trust show with all options displays all attributes
        """
        addomain = ad_domain(multihost)

        # adding external trust
        add_external_trust(multihost)

        # ipa trust-show
        opt_list = ['--all', '--rights', '--raw']
        cmd = ipa_trust_show(multihost.master, addomain, opt_list)
        print "ipa trust-show --all --rights --raw\n", cmd.stdout_text

        # verifying trust show output
        if all(x in cmd.stdout_text for x in ["incoming",
                                              "outgoing",
                                              "ipantsecurityidentifier",
                                              "ipantsupportedencryptiontypes",
                                              "ipanttrustauthincoming",
                                              "ipanttrustpartner",
                                              "ipanttrustposixoffset",
                                              "objectclass",
                                              "attributelevelrights",
                                              "cn",
                                              "ipantflatname"]):
            print "Trust show with --all --rights --raw " \
                  "option works as expected"
        else:
            pytest.fail(
                "Trust show --all --rights --raw fails\n",
                pytrace=False)

    def test_0015_verifying_trust_with_two_way_option(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check two way transitive trust works
        """
        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])

        # trust-add
        opt_list = ['--type=ad', '--two-way=true', '--external=true']
        passwd = ad1.ssh_password
        cmd = ipa_trust_add(multihost.master, forwardzone, ad1.ssh_username, opt_list, passwd)
        print "ipa trust-add\n", cmd.stdout_text

        if ("Trust type: Non-transitive external "
            "trust to a domain in another Active Directory forest" and "Trust direction: Two-way trust") in cmd.stdout_text:
            print "Expected Result:\n Non transitive external" \
                  " trust is established with --two-way=true option\n"
        else:
            pytest.xfail("External trust not established")

    def test_0016_verifying_trust_delete(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check external trust is deleted
        """
        addomain = ad_domain(multihost)

        # adding external trust
        add_external_trust(multihost)

        # Delete Trust
        cmd = multihost.master.run_command(['ipa', 'trust-del',
                                            addomain], raiseonerr=False)
        print cmd.stdout_text
        if "Deleted trust" in cmd.stdout_text:
            print "Trust deleted successfully\n"
        else:
            pytest.xfail("External trust not deleted")

    def test_0017_verifying_trust_with_secret_option(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check external trust is added with trust secret option.
        """
        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])
        multihost.secret = "Passwd123"
        multihost.master.kinit_as_admin()
        expect_script = 'set timeout 15\n'
        expect_script += 'spawn ipa trust-add ' + \
                         forwardzone + ' --admin ' + \
                         ad1.ssh_username + \
                         ' --type=ad' \
                         ' --external=True' \
                         ' --trust-secret\n'
        expect_script += 'expect "Active Directory' \
                         ' domain administrator\'s password:"\n'
        expect_script += 'send "%s\r"\n' % ad1.ssh_password
        expect_script += 'expect "Shared secret for the trust:"\n'
        expect_script += 'send "%s\r"\n' % multihost.secret
        expect_script += 'expect "Trust status: Waiting' \
                         ' for confirmation by remote side"\n'
        expect_script += 'expect EOF\n'
        output = multihost.master.expect(expect_script)

    def test_0018_verifying_ssh_from_client(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check trusted domain users can ssh
        """
        multihost.password = multihost.master.config.admin_pw
        multihost.aduser = 'etuser1'

        # adding external trust
        add_external_trust(multihost)

        # user ssh from client
        ssh_from_client(multihost)

    def test_0019_verifying_access(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        Check trusted domain users have access to ipa resources.
        """
        multihost.password = multihost.master.config.admin_pw
        realm = multihost.master.domain.realm
        ipadomain = multihost.master.hostname

        # adding external trust
        add_external_trust(multihost)
        multihost.master.kinit_as_admin()
        exp_out1 = "HTTP/" + ipadomain + '@' + realm + ':' ' kvno' + ' ='
        multihost.master.qerun(['kvno', 'HTTP' + '/' + multihost.master.hostname +
                                '@' + realm], exp_output=exp_out1)
        exp_out2 = "CIFS/" + ipadomain + '@' + realm + ':' ' kvno' + ' ='
        multihost.master.qerun(['kvno', 'CIFS' + '/' + multihost.master.hostname +
                                '@' + realm], exp_output=exp_out2)

    def test_0020_adding_external_trust_with_incorrect_option(self, multihost):
        """
        @Title: IDM-IPA-TC: External Trust with Active Directory domain:
        external trust add fails when incorrect value is specified
        """
        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])
        expectoutput = "ipa: ERROR: invalid 'external': must be True or False"

        # trust-add
        opt_list = ['--type=ad', '--external=test']
        passwd = ad1.ssh_password
        cmd = ipa_trust_add(multihost.master, forwardzone, ad1.ssh_username, opt_list, passwd, raiseonerr=False)
        print "ipa trust-add\n", cmd.stderr_text

        if expectoutput in cmd.stderr_text:
            print "Failed as expected"
        else:
            pytest.xfail("External trust established with invalid input")

    def class_teardown(self, multihost):
        """ Teardown for class """
