"""
This covers the test cases for one way trust feature
"""
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.shared.utils import (disable_dnssec, dnsforwardzone_add,
                                      add_dnsforwarder, sssd_cache_reset)
from ipa_pytests.qe_install import adtrust_install
import pytest
import time

aduser = 'aduser1'
aduser_pwd = 'Secret123'


class TestOneWay(object):
    """
    This covers the test cases for RFE bugzilla 1145748
    """
    def class_setup(self, multihost):
        """ Setup for class """
        disable_dnssec(multihost.master)

        adtrust_install(multihost.master)

        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])
        domain = multihost.master.domain.name

        etchosts = '/etc/hosts'
        etchostscfg = multihost.master.get_file_contents(etchosts)
        etchostscfg += '\n' + ad1.ip + ' ' + ad1.hostname + '\n'
        multihost.master.put_file_contents(etchosts, etchostscfg)

        dnsforwardzone_add(multihost.master, forwardzone, ad1.ip)
        time.sleep(60)

        add_dnsforwarder(ad1, domain, multihost.master.ip)
        #add_dnsforwarder(ad1, domain, multihost.master.external_ip)
        time.sleep(60)

        cmd = multihost.master.run_command('dig +short SRV _ldap._tcp.' +
                                           forwardzone, raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if ad1.hostname in cmd.stdout_text:
            print("dns resolution passed for ad domain")
        else:
            pytest.xfail("dns resolution failed for ad domain")
        cmd = multihost.master.run_command('dig +short SRV @' + ad1.ip +
                                           ' _ldap._tcp.' + domain,
                                           raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if domain in cmd.stdout_text:
            print("dns resolution passed for ipa domain")
        else:
            pytest.xfail("dns resolution failed for ipa domain")

    def test_001_one_way_trust_add(self, multihost):
        """
        @Title: IDM-IPA-TC: one way trust : one way trust addition and coverage of bzs 1250190 and 1250135
        """
        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])
        domain = multihost.master.domain.name
        realm = multihost.master.domain.realm

        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa', 'trust-add', forwardzone,
                                            '--admin', ad1.ssh_username,
                                            '--type=ad'],
                                           stdin_text=ad1.ssh_password,
                                           raiseonerr=False)
        print(cmd.stdout_text)
        if "Trust direction: Trusting forest" in cmd.stdout_text:
            print("One way trust established successfully")
        else:
            pytest.xfail("One way trust addition failed")
        print(cmd.stderr_text)
        print("waiting for 60 seconds")
        time.sleep(60)
        cmd = multihost.master.run_command('ipactl restart', raiseonerr=False)
        print(cmd.stdout_text)
        print("waiting for 60 seconds")
        time.sleep(60)
        sssd_cache_reset(multihost.master)
        time.sleep(10)
        cmd = multihost.master.run_command(['id', aduser + '@' + forwardzone],
                                           raiseonerr=False)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        if aduser in cmd.stdout_text:
            print("AD user resolved on IPA")
        else:
            pytest.xfail("AD user not resolved on IPA ")

        # Following section tries that krb tkts not issued to IPA users from AD in one way trust

        multihost.master.run_command(['kdestroy', '-A'], raiseonerr=False)
        multihost.master.kinit_as_admin()
        multihost.master.run_command(['kvno', '-S', 'host',
                                      multihost.master.hostname],
                                     raiseonerr=False)
        cmd = multihost.master.run_command(['kvno', '-S', 'cifs',
                                            ad1.external_hostname],
                                           raiseonerr=False)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        exp_output = "not found in Kerberos database while getting credentials for cifs"
        if exp_output in cmd.stderr_text:
            print("krb tkt for IPA user not granted from AD domain")
        else:
            pytest.xfail(" krb tkt for IPA user granted from AD domain ")

        # Verifying Bugzilla 1250190

        cmd = multihost.master.run_command(['ipa', 'trustdomain-find',
                                            forwardzone], raiseonerr=False)
        ad_doms = cmd.stdout_text.split("\n")
        root_child_domain = []
        for dom in ad_doms:
            if "Domain name:" in dom:
                root_child_domain.append(dom.split(": ")[1])
        root_domain = root_child_domain[0]
        child_domain = root_child_domain[1]
        root_domain_id_range = root_domain.upper() + '_id_range'
        child_domain_id_range = child_domain.upper() + '_id_range'

        cmd = multihost.master.run_command(['ipa', 'idrange-show',
                                            root_domain_id_range],
                                           raiseonerr=False)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        if "Range type: Active Directory domain range" in cmd.stdout_text:
            print("id range found for root domain")
        else:
            pytest.xfail("id range not found for root domain")

        cmd = multihost.master.run_command(['ipa', 'idrange-show',
                                            child_domain_id_range],
                                           raiseonerr=False)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        if "Range type: Active Directory domain range" in cmd.stdout_text:
            print("id range found for child domain ")
        else:
            pytest.xfail("Bugzilla 1250190 found")

        cmd = multihost.master.run_command(['getent', 'passwd', aduser + '@' +
                                            root_domain], raiseonerr=False)
        print(cmd.stdout_text)
        if aduser in cmd.stdout_text:
            print("gentent working fine for root domain")
        else:
            pytest.xfail("getent failed for root domain")

        cmd = multihost.master.run_command(['getent', 'passwd', aduser + '@' +
                                            child_domain], raiseonerr=False)
        print(cmd.stdout_text)
        if aduser in cmd.stdout_text:
            print("gentent working fine for child domain")
        else:
            pytest.xfail("Bugzilla 1250190 found")

        # Deleting trust-added
        cmd = multihost.master.run_command(['ipa', 'trust-del', forwardzone],
                                           raiseonerr=False)
        print(cmd.stdout_text)
        if "Deleted trust" in cmd.stdout_text:
            print("One way trust deleted successfully")
        else:
            pytest.xfail("One way trust deletion failed")

        # Verifying Bugzilla 1250135
        # It verifies that two way trust added after removing oneway trust

        cmd = multihost.master.run_command(['ipa', 'trust-add', forwardzone,
                                            '--admin', ad1.ssh_username,
                                            '--type=ad',
                                            '--two-way=True'],
                                           stdin_text=ad1.ssh_password,
                                           raiseonerr=False)
        print(cmd.stdout_text)

        cmd = multihost.master.run_command(['ipa', 'trust-show', forwardzone],
                                           raiseonerr=False)
        print(cmd.stdout_text)
        if "Trust direction: Two-way trust" in cmd.stdout_text:
            print("Two way trust establised successfully")
        else:
            pytest.xfail("Two way trust addition failed")
        print("waiting for 60 seconds")
        time.sleep(60)
        cmd = multihost.master.run_command('ipactl restart', raiseonerr=False)
        print(cmd.stdout_text)
        print("waiting for 60 seconds")
        time.sleep(60)

        # Following section tries that krb tkts issued to IPA users from AD in two way trust scenario

        multihost.master.run_command(['kdestroy', '-A'], raiseonerr=False)
        multihost.master.kinit_as_admin()
        multihost.master.run_command(['kvno', '-S', 'host',
                                      multihost.master.hostname],
                                     raiseonerr=False)
        multihost.master.run_command(['kvno', '-S', 'cifs',
                                      ad1.external_hostname],
                                     raiseonerr=False)
        cmd = multihost.master.run_command(['klist'], raiseonerr=False)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        exp_output = "krbtgt/" + forwardzone.upper() + '@' + forwardzone.upper()
        if exp_output in cmd.stdout_text:
            print("krb tkt for IPA user granted from AD domain")
        else:
            pytest.xfail(" krb tkt for IPA user not granted from AD domain ")

        # Cleanup
        cmd = multihost.master.run_command(['ipa', 'trust-del', forwardzone],
                                           raiseonerr=False)
        print(cmd.stdout_text)
        if "Deleted trust" in cmd.stdout_text:
            print("Two way trust deleted successfully")
        else:
            pytest.xfail("Two way trust deletion failed")

    def test_002_one_way_trust_add(self, multihost):
        """
        @Title: IDM-IPA-TC: one way trust : two way trust addition and coverage of bz 1250135
        """
        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])
        realm = multihost.master.domain.realm

        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa', 'trust-add', forwardzone,
                                            '--admin', ad1.ssh_username,
                                            '--type=ad',
                                            '--two-way=True'],
                                           stdin_text=ad1.ssh_password,
                                           raiseonerr=False)
        print(cmd.stdout_text)

        cmd = multihost.master.run_command(['ipa', 'trust-show', forwardzone],
                                           raiseonerr=False)
        print(cmd.stdout_text)
        if "Trust direction: Two-way trust" in cmd.stdout_text:
            print("Two way trust establised successfully")
        else:
            pytest.xfail("Two way trust addition failed")
        print("waiting for 60 seconds")
        time.sleep(60)
        cmd = multihost.master.run_command('ipactl restart', raiseonerr=False)
        print(cmd.stdout_text)
        print("waiting for 60 seconds")
        time.sleep(60)

        # Following section tries that krb tkts issued to AD users from IPA in two way trust scenario

        multihost.master.run_command(['kdestroy', '-A'], raiseonerr=False)
        multihost.master.run_command(['kinit', aduser + '@' +
                                      forwardzone.upper()],
                                     stdin_text="Secret123",
                                     raiseonerr=False)
        multihost.master.run_command(['kvno', '-S', 'host',
                                      multihost.master.hostname],
                                     raiseonerr=False)
        cmd = multihost.master.run_command(['klist'], raiseonerr=False)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        exp_output = "krbtgt/" + realm + '@' + forwardzone.upper()
        if exp_output in cmd.stdout_text:
            print("krb tkt for AD user granted from IPA domain")
        else:
            pytest.xfail(" krb tkt for AD user not granted from IPA domain ")

        # Deleting trust
        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa', 'trust-del', forwardzone],
                                           raiseonerr=False)
        print(cmd.stdout_text)
        if "Deleted trust" in cmd.stdout_text:
            print("Two way trust deleted successfully")
        else:
            pytest.xfail("Two way trust deletion failed")

        # Adding oneway trust for verification of bugzilla 1250135
        # It verifies that oneway trust added after removing two way trust

        cmd = multihost.master.run_command(['ipa', 'trust-add', forwardzone,
                                            '--admin', ad1.ssh_username,
                                            '--type=ad'],
                                           stdin_text=ad1.ssh_password,
                                           raiseonerr=False)
        print(cmd.stdout_text)
        if "Trust direction: Trusting forest" in cmd.stdout_text:
            print("One way trust establised successfully")
        else:
            pytest.xfail("One way trust addition failed")
        print(cmd.stderr_text)
        print("waiting for 60 seconds")
        time.sleep(60)
        cmd = multihost.master.run_command('ipactl restart', raiseonerr=False)
        print(cmd.stdout_text)
        print("waiting for 60 seconds")
        time.sleep(60)

        # Following section tries that krb tkts issued to AD users from IPA domain in one way trust scenario

        multihost.master.run_command(['kdestroy', '-A'], raiseonerr=False)
        multihost.master.run_command(['kinit', aduser + '@' +
                                      forwardzone.upper()],
                                     stdin_text="Secret123",
                                     raiseonerr=False)
        multihost.master.run_command(['kvno', '-S', 'host',
                                      multihost.master.hostname],
                                     raiseonerr=False)
        cmd = multihost.master.run_command(['klist'], raiseonerr=False)
        print(cmd.stdout_text)
        print(cmd.stderr_text)
        exp_output = "krbtgt/" + realm + '@' + forwardzone.upper()
        if exp_output in cmd.stdout_text:
            print("krb tkt for AD user granted from IPA domain")
        else:
            pytest.xfail(" krb tkt for AD user not granted from IPA domain ")

        # Cleanup
        multihost.master.run_command(['kdestroy', '-A'], raiseonerr=False)
        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa', 'trust-del', forwardzone],
                                           raiseonerr=False)
        print(cmd.stdout_text)
        if "Deleted trust" in cmd.stdout_text:
            print("One way trust deleted successfully")
        else:
            pytest.xfail("One way trust deletion failed")

    def class_teardown(self, multihost):
        """ Teardown for class """
