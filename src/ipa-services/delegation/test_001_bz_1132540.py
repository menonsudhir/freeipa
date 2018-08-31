"""
Overview:
Test to verify #1132540-[RFE] Expose service delegation rules in UI and CLI
Setup Requirements:
IPA Server configured on RHEL7.2
IPA Client configured on RHEL7.2
"""

import pytest


class Test_bz_1132540(object):

    """ Test Class for service add """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        master_name = multihost.master.hostname
        print("MASTER: ", master_name)
        print("CLIENT: ", multihost.client.hostname)
        multihost.tst_srv1 = 'EXAMPLE1'
        multihost.tst_srv2 = 'EXAMPLE2'
        multihost.tst_srv1_name = multihost.tst_srv1 + '/' + master_name
        multihost.tst_srv2_name = multihost.tst_srv2 + '/' + master_name
        multihost.tst_srv1_keytab = '/tmp/' + multihost.tst_srv1 + '.keytab'
        multihost.tst_srv2_keytab = '/tmp/' + multihost.tst_srv2 + '.keytab'
        multihost.srv_tgt = "target-test-example1"

        # Create setup
        multihost.master.kinit_as_admin()
        # Add service to Client
        multihost.master.qerun(['ipa', 'service-add',
                                multihost.tst_srv1_name],
                               exp_returncode=0, exp_output="Added service")
        multihost.master.qerun(['ipa', 'service-mod', multihost.tst_srv1_name,
                                '--setattr', 'krbticketflags=2097280'],
                               exp_returncode=0, exp_output="Modified service")
        multihost.master.qerun(['ipa', 'service-add', multihost.tst_srv2_name],
                               exp_returncode=0, exp_output="Added service")
        multihost.master.qerun(['ipa-getkeytab', '-s', master_name, '-k',
                                multihost.tst_srv1_keytab, '-p',
                                multihost.tst_srv1_name],
                               exp_returncode=0,
                               exp_output="Keytab successfully")
        multihost.master.qerun(['ipa-getkeytab', '-s', master_name, '-k',
                                multihost.tst_srv2_keytab, '-p',
                                multihost.tst_srv2_name],
                               exp_returncode=0,
                               exp_output="Keytab successfully")

    def test_0001_negative_expose_service_delegation(self, multihost):
        """
        IDM-IPA-TC : Services : Check if IPA cli exposes service delegation rules negative
        """
        print(multihost.tst_srv1_name)
        multihost.master.qerun(['kdestroy', '-A'], exp_returncode=0)
        multihost.master.qerun(['kinit', '-kt', multihost.tst_srv1_keytab,
                                multihost.tst_srv1_name],
                               exp_returncode=0)
        multihost.master.qerun(['kvno', '-k', multihost.tst_srv1_keytab,
                                '-U', 'admin', '-P', multihost.tst_srv1_name,
                                multihost.tst_srv2_name],
                               exp_returncode=1,
                               exp_output="constrained delegation failed")

    def test_0002_positive_expose_service_delegation(self, multihost):
        """
        IDM-IPA-TC : Services : Check if IPA cli exposes service delegation rules positive
        """
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'servicedelegationrule-add',
                                multihost.tst_srv1],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'servicedelegationtarget-add',
                                multihost.srv_tgt],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'servicedelegationrule-add-target',
                                '--servicedelegationtargets=' +
                                multihost.srv_tgt,
                                multihost.tst_srv1],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'servicedelegationrule-add-member',
                                '--principals', multihost.tst_srv1_name,
                                multihost.tst_srv1],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'servicedelegationtarget-add-member',
                                '--principals=' + multihost.tst_srv2_name,
                                multihost.srv_tgt],
                               exp_returncode=0)

    def class_teardown(self, multihost):
        """
        Cleanup
        """
        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'service-del',
                                multihost.tst_srv1_name],
                               exp_returncode=0, exp_output="Deleted service")
        multihost.master.qerun(['ipa', 'service-del',
                                multihost.tst_srv2_name],
                               exp_returncode=0, exp_output="Deleted service")
        multihost.master.qerun(['ipa', 'servicedelegationrule-del',
                                multihost.tst_srv1],
                               exp_returncode=0)
        multihost.master.qerun(['ipa', 'servicedelegationtarget-del',
                                multihost.srv_tgt],
                               exp_returncode=0)
        multihost.master.qerun(['rm', '-rf',
                                multihost.tst_srv1_keytab,
                                multihost.tst_srv2_keytab])
