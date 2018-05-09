'''
Test cases for IPA-server-docker container as IPA.
################################################################
Note: Make sure PermitRootLogin and PasswordAuthentication is
enabled on atomic host client machine in order to run the below
tests.
###############################################################
'''
import pytest
import time
from ipa_pytests.shared.utils import service_control, dnsforwardzone_add_docker
from ipa_pytests.shared.utils import sssd_cache_reset_docker, disable_dnssec_docker
from ipa_pytests.shared.utils import *
from ipa_pytests.qe_install import setup_master_docker, uninstall_master_docker
from ipa_pytests.qe_install import adtrust_install
from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.qe_install import *

aduser = 'aduser1'
aduser_pwd = 'Secret123'

class TestMaster(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print"MASTER: ", multihost.master.hostname
        # Enabling Setsebool, this change is required or else
        # installation will fail. This is introduced from
        # RHEL Atomic host 7.5.0 onwards.
        multihost.master.run_command(['setsebool', '-P',
                                      'container_manage_cgroup',
                                      '1'],  raiseonerr=False)
        multihost.master.run_command(['getsebool', 'container_manage_cgroup'],
                                      raiseonerr=False)
        time.sleep(30)
        multihost.master.run_command(['docker', 'images'])

    def test_master_0001(self, multihost):
        """@TITLE: IDM-IPA-TC : ipa-server-docker : Check if Trust can be setup on IPA master using docker image"""
        master = multihost.master
        container = 'ipadocker'
        masterip = multihost.master.ip
        setup_master_docker(master)
        time.sleep(120)
        docker_service_restart(master, container)
        docker_service_status(master, container)
        docker_kinit_as_admin(master, container)

        # Disable DNSSEC
        disable_dnssec_docker(multihost.master, container)

        # Add DNSForwardZone details at AD for IPA Domain
        ad1 = multihost.ads[0]
        adhost = multihost.ads[0].hostname
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])
        realm = multihost.master.domain.realm
        domain = multihost.master.domain.name

        # Adding Ad details to master system hosts file
        etchosts = '/etc/hosts'
        etchostscfg = multihost.master.get_file_contents(etchosts)
        etchostscfg += '\n' + ad1.ip + ' ' + ad1.hostname + '\n'
        multihost.master.put_file_contents(etchosts, etchostscfg)

        # Add Forwardzone on IPA for AD
        dnsforwardzone_add_docker(multihost.master, forwardzone, ad1.ip, container)

        # Add DNS forwarder on AD machine for IPA domain
        add_dnsforwarder(ad1, domain, masterip)
        time.sleep(60)

        # Dig command to verify DNS configuration for IPA and AD domain
        print('Checking DNS configuration for AD on IPA')
        cmd = multihost.master.run_command(paths.DOCKER + ' exec -i ' + container +
                                           ' dig +short SRV _ldap._tcp.' + forwardzone,
                                           raiseonerr=False)
        print cmd.stdout_text, cmd.stderr_text

        if ad1.hostname in cmd.stdout_text:
            print("dns resolution passed for ad domain")
        else:
            pytest.xfail("dns resolution failed for ad domain")

        print('Checking DNS configuration for IPA on AD')
        cmd = multihost.master.run_command(paths.DOCKER + ' exec -i ' + container +
                                           ' dig +short SRV @' + ad1.ip +
                                           ' _ldap._tcp.' + domain,
                                           raiseonerr=False)
        print cmd.stdout_text, cmd.stderr_text
        if domain in cmd.stdout_text:
            print("dns resolution passed for ipa domain")
        else:
            pytest.xfail("dns resolution failed for ipa domain")

        # Ad-Trust Install
        adtrust_install(master)

        # Trust-add
        cmd = multihost.master.run_command([paths.DOCKER, 'exec', '-i',
                                            container,
                                            'ipa', 'trust-add', forwardzone,
                                            '--admin', ad1.ssh_username,
                                            '--type=ad',
                                            '--two-way=True'],
                                           stdin_text=ad1.ssh_password,
                                           raiseonerr=False)
        print cmd.stdout_text

        # Verify added Trust
        cmd = multihost.master.run_command([paths.DOCKER, 'exec', '-i',
                                            container,
                                            'ipa', 'trust-show', forwardzone],
                                           raiseonerr=False)
        print cmd.stdout_text
        if "Trust direction: Two-way trust" in cmd.stdout_text:
            print "Two way trust establised successfully"
        else:
            pytest.xfail("Two way trust addition failed")
        print "waiting for 60 seconds"
        time.sleep(60)

        # Verifying Basics work after trust-add
        docker_service_restart(master, container)
        docker_service_status(master, container)
        docker_kinit_as_admin(master, container)

    def test_master_0002(self, multihost):
        """@TITLE: IDM-IPA-TC : ipa-server-docker : Check if id command works on IPA master using docker image"""
        ad1 = multihost.ads[0]
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])
        master = multihost.master
        container = 'ipadocker'

        print "waiting for 60 seconds"
        time.sleep(60)
        sssd_cache_reset_docker(multihost.master, container)
        time.sleep(60)
        cmd = multihost.master.run_command(paths.DOCKER + ' exec -i ' + container +
                                           ' id ' + aduser + '@' + forwardzone,
                                           raiseonerr=False)
        print cmd.stdout_text, cmd.stderr_text
        if cmd.returncode == 0:
            print "AD user resolved on IPA"
        else:
            pytest.xfail("AD user not resolved on IPA ")

    def test_master_0003(self, multihost):
        """@TITLE: IDM-IPA-TC : ipa-server-docker : Check if Trust can be deleted on IPA master using docker image"""
        ad1 = multihost.ads[0]
        master = multihost.master
        container = 'ipadocker'
        forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])

        # Deleting trust
        docker_kinit_as_admin(master, container)
        cmd = multihost.master.run_command([paths.DOCKER, 'exec', '-i',
                                            container,
                                            'ipa', 'trust-del', forwardzone],
                                           raiseonerr=False)
        print cmd.stdout_text
        if "Deleted trust" in cmd.stdout_text:
            print "Two way trust deleted successfully"
        else:
            pytest.xfail("Two way trust deletion failed")

    def class_teardown(self, multihost):
        """Teardown"""
        print('This is Teardown')
        master = multihost.master
        uninstall_master_docker(master)
        pass
