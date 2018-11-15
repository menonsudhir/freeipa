"""
Overview:
Test suite to verify sudo options
"""

import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.sudo_utils import sudorule_add, sudorule_mod, sudorule_add_option, sudorule_find, sudorule_del
from ipa_pytests.shared.utils import sssd_cache_reset

low_prior_rule = "sudorule1"
high_prior_rule = 'sudorule2'
low_priority_order = 2
high_priority_order = 12


class TestBugCheck(object):
    """ Test Class """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)
        # print("CLIENT: ", multihost.client.hostname)

    def test_0001_bz1232950(self, multihost):
        """
        IDM-IPA-TC : Sudo : Test to check Bug 1232950 - [IPA/IdM] sudoOrder not honored as expected
        """
        # requirement:no sudorules should be present when the function is called
        multihost.master.kinit_as_admin()
        sudorule_add(multihost.master, low_prior_rule, usercat='all', hostcat='all', cmdcat='all',
                     runasusercat='all', runasgroupcat='all', order=low_priority_order)
        sudorule_add(multihost.master, high_prior_rule, usercat='all', hostcat='all', cmdcat='all',
                     runasusercat='all', runasgroupcat='all', order=high_priority_order)
        sudorule_add_option(multihost.master, high_prior_rule, '!authenticate')
        print(sudorule_find(multihost.master))
        sssd_cache_reset(multihost.master)
        # expect_script = 'set timeout 15\n'
        # expect_script += 'spawn sudo -l -U admin\n'
        # expect_script += 'expect EOF\n'
        #output = multihost.master.expect(expect_script)
        cmd_run = multihost.master.run_command("sudo -l -U admin")
        # op = output.stdout_text
        op = cmd_run.stdout_text
        # print("EXPECT FUNCTION OUTPUT")
        print("Checking sudo policy : Running sudo -l -U admin")
        print(op)

        op_list = op.strip().splitlines()
        if op_list[-1].__contains__("NOPASSWD"):
            print ("Correct order seen!")
        else:
            pytest.fail("Error: Wrong order %s" % op_list[-1])
        sudorule_mod(multihost.master, low_prior_rule,
                     order=high_priority_order+1)
        sssd_cache_reset(multihost.master)
        print (sudorule_find(multihost.master))
        # expect_script1 = 'set timeout 15\n'
        # expect_script1 += 'spawn sudo -l -U admin\n'
        # expect_script1 += 'expect EOF\n'
        # output1 = multihost.master.expect(expect_script1)
        cmd_run = multihost.master.run_command("sudo -l -U admin")
        # op1 = output1.stdout_text
        op = cmd_run.stdout_text
        # print("EXPECT FUNCTION OUTPUT")
        print("Checking sudo policy again : Running sudo -l -U admin")
        # print(op1)
        print(op)
        check = sudorule_find(multihost.master)
        print(check.stdout_text)
        op_list = op.strip().splitlines()
        if op_list[-2].__contains__("NOPASSWD"):
            print ("Correct order seen!")
        else:
            pytest.fail("Error: Wrong order %s" % op_list[-2])

    def class_teardown(self, multihost):
        """ Full suite teardown """
        multihost.master.kinit_as_admin()
        sudorule_del(multihost.master, high_prior_rule)
        sudorule_del(multihost.master, low_prior_rule)
