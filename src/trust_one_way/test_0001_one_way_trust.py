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
        forwardzone = '.'.join(ad1.hostname.split(".")[1:])
        domain = multihost.master.domain.name

        etchosts = '/etc/hosts'
        etchostscfg = multihost.master.get_file_contents(etchosts)
        etchostscfg += '\n' + ad1.ip + ' ' + ad1.hostname + '\n'
        multihost.master.put_file_contents(etchosts, etchostscfg)

        dnsforwardzone_add(multihost.master, forwardzone, ad1.ip)

        add_dnsforwarder(ad1, domain, multihost.master.ip)

        multihost.master.qerun('dig +short SRV _ldap._tcp.' + forwardzone)
        multihost.master.qerun(
            'dig +short SRV @' + ad1.ip + ' _ldap._tcp.' + domain)

    def test_001_one_way_trust_add(self, multihost):
        """
        @Title: IDM-IPA-TC: one way trust : one way trust addition and coverage of bzs 1250190 and 1250135
        """
        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.hostname.split(".")[1:])

        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'trust-add', forwardzone,
                                '--admin', ad1.ssh_username,
                                '--type=ad'],
                               stdin_text=ad1.ssh_password)
        multihost.master.qerun('ipactl restart')
        sssd_cache_reset(multihost.master)
        time.sleep(10)
        cmd = multihost.master.qerun(['id', aduser + '@' + forwardzone])
        assert aduser in cmd.stdout_text, 'AD user not resolved on IPA'

        # Following section tries that krb tkts not issued to IPA users from AD in one way trust
        multihost.master.qerun(['kdestroy', '-A'])
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['kvno', '-S', 'host',
                                multihost.master.hostname])
        cmd = multihost.master.qerun(['kvno', '-S', 'cifs', ad1.hostname],
                                     exp_returncode=1)
        exp_output = "not found in Kerberos database while getting credentials for cifs"
        assert exp_output in cmd.stderr_text, \
            'krb tkt for IPA user granted from AD domain'

        # Verifying Bugzilla 1250190

        cmd = multihost.master.qerun(['ipa', 'trustdomain-find', forwardzone])
        ad_doms = cmd.stdout_text.split("\n")
        root_child_domain = []
        for dom in ad_doms:
            if "Domain name:" in dom:
                root_child_domain.append(dom.split(": ")[1])
        root_domain = root_child_domain[0]
        child_domain = root_child_domain[1]
        root_domain_id_range = root_domain.upper() + '_id_range'
        child_domain_id_range = child_domain.upper() + '_id_range'

        cmd = multihost.master.qerun(['ipa', 'idrange-show',
                                      root_domain_id_range])
        assert 'Range type: Active Directory domain range' in cmd.stdout_text, \
            'id range not found for root domain'

        cmd = multihost.master.qerun(['ipa', 'idrange-show',
                                      child_domain_id_range])
        assert 'Range type: Active Directory domain range' in cmd.stdout_text,\
            'Bugzilla 1250190 found'

        cmd = multihost.master.qerun(['getent', 'passwd',
                                      aduser + '@' + root_domain])
        assert aduser in cmd.stdout_text, 'getent failed for root domain'

        cmd = multihost.master.qerun(['getent', 'passwd',
                                      aduser + '@' + child_domain])
        assert aduser in cmd.stdout_text, 'Bugzilla 1250190 found'

        # Deleting trust-added
        multihost.master.qerun(['ipa', 'trust-del', forwardzone])

        # Verifying Bugzilla 1250135
        # It verifies that two way trust added after removing oneway trust

        multihost.master.qerun(['ipa', 'trust-add', forwardzone,
                                '--admin', ad1.ssh_username,
                                '--type=ad',
                                '--two-way=True'], stdin_text=ad1.ssh_password)
        cmd = multihost.master.qerun(['ipa', 'trust-show', forwardzone])
        assert 'Trust direction: Two-way trust' in cmd.stdout_text, \
            'Two way trust addition failed'
        multihost.master.qerun('ipactl restart')

        # Following section tries that krb tkts issued to IPA users from AD in two way trust scenario

        multihost.master.qerun(['kdestroy', '-A'])
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['kvno', '-S', 'host',
                                multihost.master.hostname])
        multihost.master.qerun(['kvno', '-S', 'cifs', ad1.hostname])
        cmd = multihost.master.qerun(['klist'])
        exp_output = "krbtgt/" + forwardzone.upper() + '@' + forwardzone.upper()
        assert exp_output in cmd.stdout_text, \
            'krb tkt for IPA user not granted from AD domain'

        # Cleanup
        multihost.master.qerun(['ipa', 'trust-del', forwardzone])

    def test_002_one_way_trust_add(self, multihost):
        """
        @Title: IDM-IPA-TC: one way trust : two way trust addition and coverage of bz 1250135
        """
        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.hostname.split(".")[1:])
        realm = multihost.master.domain.realm

        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'trust-add', forwardzone,
                                '--admin', ad1.ssh_username,
                                '--type=ad',
                                '--two-way=True'],
                               stdin_text=ad1.ssh_password)
        multihost.master.qerun(
            ['ipa', 'trust-show', forwardzone],
            exp_output='Trust direction: Two-way trust')
        multihost.master.qerun('ipactl restart')

        # Following section tries that krb tkts issued to AD users from IPA in two way trust scenario

        multihost.master.qerun(['kdestroy', '-A'])
        multihost.master.qerun(['kinit', aduser + '@' + forwardzone.upper()],
                               stdin_text="Secret123")
        multihost.master.qerun(['kvno', '-S', 'host',
                                multihost.master.hostname])
        cmd = multihost.master.qerun(['klist'])
        exp_output = "krbtgt/" + realm + '@' + forwardzone.upper()
        assert exp_output in cmd.stdout_text, \
            'krb tkt for AD user not granted from IPA domain'

        # Deleting trust
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'trust-del', forwardzone])

        # Adding oneway trust for verification of bugzilla 1250135
        # It verifies that oneway trust added after removing two way trust

        multihost.master.qerun(['ipa', 'trust-add', forwardzone,
                                '--admin', ad1.ssh_username,
                                '--type=ad'],
                                stdin_text=ad1.ssh_password)
        cmd = multihost.master.qerun('ipactl restart')

        # Following section tries that krb tkts issued to AD users from IPA domain in one way trust scenario

        multihost.master.qerun(['kdestroy', '-A'])
        multihost.master.qerun(['kinit', aduser + '@' + forwardzone.upper()],
                               stdin_text="Secret123")
        multihost.master.qerun(['kvno', '-S', 'host',
                                multihost.master.hostname])
        cmd = multihost.master.qerun(['klist'])
        exp_output = "krbtgt/" + realm + '@' + forwardzone.upper()
        assert exp_output in cmd.stdout_text, \
            'krb tkt for AD user not granted from IPA domain'

        # Cleanup
        multihost.master.qerun(['kdestroy', '-A'])
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'trust-del', forwardzone])
