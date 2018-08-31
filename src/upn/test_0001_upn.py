"""
This covers the test cases for upn feature
"""
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.shared.utils import (service_control)
from ipa_pytests.shared.utils import (disable_dnssec, dnsforwardzone_add,
                                      add_dnsforwarder, sssd_cache_reset)
from ipa_pytests.qe_install import adtrust_install
import pytest
import time

aduser = 'testaduser'
aduser_pwd = 'Secret123'
upn_user = 'testupnuser'
upn_suffix = 'testupnsuffix' # It seems upn suffixes can not be added via command prompt, so 'testupnsuffix' is added ahead in GUI.
upn_full = upn_user + '@' + upn_suffix

class TestUPN(object):
    """
    This covers the test cases for RFE bugzilla 1287194
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

        add_dnsforwarder(ad1, domain, multihost.master.ip)

        cmd = multihost.master.run_command('dig +short SRV _ldap._tcp.' +
                                           forwardzone,
                                           raiseonerr=False)
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

    def test_0001_upn_check_one_way_trust(self, multihost):
        """
        @Title: IDM-IPA-TC: UPN : Check if UPN suffixes are displayed in ipa trust show with one way trust
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
        print(cmd.stdout_text, cmd.stderr_text)
        if "Trust direction: Trusting forest" in cmd.stdout_text:
            print("One way trust established successfully")
        else:
            pytest.xfail("One way trust addition failed")

        multihost.master.run_command(['ipa', 'trust-fetch-domains', forwardzone],
                                     raiseonerr=False)
        cmd = multihost.master.run_command(['ipa', 'trust-show', forwardzone],
                                     raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if upn_suffix in cmd.stdout_text:
            print("UPN suffix is seen as expected")
        else:
            pytest.xfail("UPN suffix is not seen as expected")
        # Cleanup
        cmd = multihost.master.run_command(['ipa', 'trust-del', forwardzone],
                                           raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if "Deleted trust" in cmd.stdout_text:
            print("One way trust deleted successfully")
        else:
            pytest.xfail("One way trust deletion failed")

    def test_0002_upn_check_two_way_trust(self, multihost):
        """
        @Title: IDM-IPA-TC: UPN : Check if UPN suffixes are displayed in ipa trust show with two way trust
        """
        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])
        domain = multihost.master.domain.name
        realm = multihost.master.domain.realm

        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa', 'trust-add', forwardzone,
                                            '--admin', ad1.ssh_username,
                                            '--type=ad',
                                            '--two-way=True'],
                                           stdin_text=ad1.ssh_password,
                                           raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if "Trust direction: Two-way trust" in cmd.stdout_text:
            print("Two way trust established successfully")
        else:
            pytest.xfail("Two way trust addition failed")

        multihost.master.run_command(['ipa', 'trust-fetch-domains', forwardzone],
                                     raiseonerr=False)
        cmd = multihost.master.run_command(['ipa', 'trust-show', forwardzone],
                                     raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if upn_suffix in cmd.stdout_text:
            print("UPN suffix is seen as expected")
        else:
            pytest.xfail("UPN suffix is not seen as expected")
        # Cleanup
        cmd = multihost.master.run_command(['ipa', 'trust-del', forwardzone],
                                           raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if "Deleted trust" in cmd.stdout_text:
            print("Two way trust deleted successfully")
        else:
            pytest.xfail("Two way trust deletion failed")

    def test_0003_upn_check_external_trust(self, multihost):
        """
        @Title: IDM-IPA-TC: UPN : Check if UPN suffixes are displayed in ipa trust show with external trust
        """
        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])
        domain = multihost.master.domain.name
        realm = multihost.master.domain.realm

        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa', 'trust-add', forwardzone,
                                            '--admin', ad1.ssh_username,
                                            '--type=ad',
                                            '--external=True'],
                                           stdin_text=ad1.ssh_password,
                                           raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if "Trust type: Non-transitive external trust" in cmd.stdout_text:
            print("External trust established successfully")
        else:
            pytest.xfail("External trust addition failed")

        multihost.master.run_command(['ipa', 'trust-fetch-domains', forwardzone],
                                     raiseonerr=False)
        cmd = multihost.master.run_command(['ipa', 'trust-show', forwardzone],
                                           raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if upn_suffix in cmd.stdout_text:
            print("UPN suffix is seen as expected")
        else:
            pytest.xfail("UPN suffix is not seen as expected")
        # Cleanup
        cmd = multihost.master.run_command(['ipa', 'trust-del', forwardzone],
                                           raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if "Deleted trust" in cmd.stdout_text:
            print("External trust deleted successfully")
        else:
            pytest.xfail("External trust deletion failed")

    def test_0004_upn_check_getent_passwd_id_kinit_commands(self, multihost):
        """
        @Title: IDM-IPA-TC: UPN : Check if UPN works with getent passwd id and kinit command output
        """
        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])
        domain = multihost.master.domain.name
        realm = multihost.master.domain.realm

        # Add and set UPN of the ad user
        cmd = ad1.run_command('dsget user "cn=%s,cn=Users,dc=%s,dc=%s"' %
                             (aduser, forwardzone.split(".")[0], forwardzone.split(".")[1]),
                              raiseonerr=False)
        print("dsget return code is: %s" % cmd.returncode)
        print(cmd.stdout_text, cmd.stderr_text)
        if cmd.returncode == 1:
            cmd = ad1.run_command('dsrm "cn=%s,cn=Users,dc=%s,dc=%s" -noprompt' %
                                 (aduser, forwardzone.split(".")[0], forwardzone.split(".")[1]),
                                  raiseonerr=False)
            print("dsrm return code is: %s" % cmd.returncode)
            print(cmd.stdout_text, cmd.stderr_text)
        cmd = ad1.run_command('dsadd user "cn=%s,cn=Users,dc=%s,dc=%s" -pwd %s -upn %s' %
                             (aduser, forwardzone.split(".")[0], forwardzone.split(".")[1], aduser_pwd, upn_full),
                              raiseonerr=False)
        print("dsadd return code is: %s" % cmd.returncode)
        print(cmd.stdout_text, cmd.stderr_text)
        if "dsadd succeeded" in cmd.stdout_text:
            print("AD user add and UPN set successfully")
        else:
            pytest.xfail("AD user add and UPN failed")

        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa', 'trust-add', forwardzone,
                                            '--admin', ad1.ssh_username,
                                            '--type=ad'],
                                           stdin_text=ad1.ssh_password,
                                           raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if "Trust direction: Trusting forest" in cmd.stdout_text:
            print("One way trust established successfully")
        else:
            pytest.xfail("One way trust addition failed")

        multihost.master.run_command(['ipa', 'trust-fetch-domains', forwardzone],
                                     raiseonerr=False)
        cmd = multihost.master.run_command(['ipa', 'trust-show', forwardzone],
                                           raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if upn_suffix in cmd.stdout_text:
            print("UPN suffix is seen as expected")
        else:
            pytest.xfail("UPN suffix is not seen as expected")
        # Restart sssd
        time.sleep(60)
        service_control(multihost.master, 'sssd', 'stop')
        multihost.master.run_command(['rm', '-rf', '/var/lib/sss/{db,mc}/*'], 
                                     raiseonerr=False)
        service_control(multihost.master, 'sssd', 'start')
        time.sleep(60)
        # Check getent passwd command output
        cmd = multihost.master.run_command(['getent', 'passwd', upn_full],
                                           raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        aduser_full = aduser + '@' + forwardzone
        aduser_hd = '/home/' + forwardzone + '/' + aduser
        if aduser_full and aduser_hd in cmd.stdout_text:
            print("Getent passwd with UPN diplays the actual username and home dir successfully")
        else:
            pytest.xfail("Getent passwd with UPN diplaying the actual username and home dir failed")
        # Check id command output
        cmd = multihost.master.run_command(['id', upn_full],
                                           raiseonerr=False)
        aduser_full = aduser + '@' + forwardzone
        if aduser_full in cmd.stdout_text:
            print("Id command with UPN diplays the actual username successfully")
        else:
            pytest.xfail("Id command with UPN diplaying the actual username failed")
        # Check kinit
        cmd = multihost.master.run_command('kinit -E ' + upn_full + '@' + forwardzone.upper(),
                                           stdin_text=aduser_pwd,
                                           raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        cmd = multihost.master.run_command('klist',
                                           raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        aduser_full = aduser + '@' + forwardzone.upper()
        if aduser_full in cmd.stdout_text:
            print("Kinit with UPN and shows actual user principal as expected")
        else:
            pytest.xfail("Kinit with UPN and shows actual user principal failed")
        # Delete aduser
        ad1.run_command('dsrm "cn=%s,cn=Users,dc=%s,dc=%s" -noprompt' %
                       (aduser, forwardzone.split(".")[0], forwardzone.split(".")[1]),
                        raiseonerr=False)

        # Cleanup
        multihost.master.kinit_as_admin()
        cmd = multihost.master.run_command(['ipa', 'trust-del', forwardzone],
                                           raiseonerr=False)
        print(cmd.stdout_text, cmd.stderr_text)
        if "Deleted trust" in cmd.stdout_text:
            print("One way trust deleted successfully")
        else:
            pytest.xfail("One way trust deletion failed")

    def class_teardown(self, multihost):
        """ Teardown for class """
