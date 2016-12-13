"""
Helper functions for sudo ipa schema
"""
import re
import time
import pytest
from ipa_pytests.shared.utils import service_control

def group_add_member(multihost, testuser, testgroup):
    """
    Add ipa user as member of ipa group
    """
    cmd = ['ipa', 'group-add', testgroup]
    multihost.master.qerun(cmd)
    cmd = ['ipa', 'group-add-member', testgroup, '--users', testuser]
    multihost.master.qerun(cmd)

def group_del(multihost, testgroup):
    """
    Delete ipa group
    """
    cmd = ['ipa', 'group-del', testgroup]
    multihost.master.qerun(cmd)

def add_sudo_command(multihost, command):
    """
    Add sudo command
    """
    cmd = ['ipa', 'sudocmd-add', command]
    multihost.master.qerun(cmd)

def del_sudo_command(multihost, command):
    """
    Delete sudo command
    """
    cmd = ['ipa', 'sudocmd-del', command]
    multihost.master.qerun(cmd)

def client_sudo_user_allowed(multihost, testuser1, testuser2, command, exp_returncode=0, exp_output=None):
    """
    Verify if testuser1 is allowed to execute command as testuser2
    """
    service_control(multihost.client, 'sssd', 'restart')
    time.sleep(10)
    cmd = multihost.client.run_command('su %s -c "sudo -u %s %s"' % (testuser1, testuser2, command), raiseonerr=False)
    if cmd.returncode != exp_returncode:
        print("Expected returncode : %s" % exp_returncode)
        print("Returned returncode : %s" % cmd.returncode)
        pytest.xfail("Return code not as expected, command run failed")

    if exp_output is not None:
        print("Expected output : %s" % exp_output)
        all_out = cmd.stdout_text + cmd.stderr_text
        if all_out and exp_output not in all_out:
            print("Returned stdout : %s" % cmd.stdout_text)
            print("Returned stderr : %s" % cmd.stderr_text)
            pytest.xfail("Return code matched but failed to verify command output")

def client_sudo_group_allowed(multihost, testuser1, testgroup2, command, exp_returncode=0, exp_output=None):
    """
    Verify if testuser1 is allowed to execute command as testgroup2
    """
    service_control(multihost.client, 'sssd', 'restart')
    time.sleep(10)
    cmd = multihost.client.run_command('su %s -c "sudo -g %s %s"' % (testuser1, testgroup2, command), raiseonerr=False)
    if cmd.returncode != exp_returncode:
        print("Expected returncode : %s" % exp_returncode)
        print("Returned returncode : %s" % cmd.returncode)
        pytest.xfail("Return code not as expected, command run failed")

    if exp_output is not None:
        print("Expected output : %s" % exp_output)
        all_out = cmd.stdout_text + cmd.stderr_text
        if all_out and exp_output not in all_out:
            print("Returned stdout : %s" % cmd.stdout_text)
            print("Returned stderr : %s" % cmd.stderr_text)
            pytest.xfail("Return code matched but failed to verify command output")

def sudorule_add_permissive_options(multihost, testsudorule, user_arg="all", host_arg="all", cmd_arg="all", runasuser_arg="all", runasgroup_arg="all"):
    """
    Add sudorule with permissive options
    """
    cmd = ['ipa', 'sudorule-add', testsudorule,
           '--usercat', user_arg,
           '--hostcat', host_arg,
           '--cmdcat', cmd_arg,
           '--runasusercat', runasuser_arg,
           '--runasgroupcat', runasgroup_arg]
    multihost.master.qerun(cmd)

def sudorule_add_defaults(multihost):
    """
    Add non-interactive default sudo rule so no password will be prompted
    """
    cmd = ['ipa', 'sudorule-add', 'defaults']
    multihost.master.qerun(cmd)
    cmd = ['ipa', 'sudorule-add-option', 'defaults', '--sudooption', '!authenticate']
    multihost.master.qerun(cmd)

def sudorule_del(multihost, testsudorule):
    """
    Delete sudo rule
    """
    cmd = ['ipa', 'sudorule-del', testsudorule]
    multihost.master.qerun(cmd)

def sudorule_add_attr(multihost, attr, testsudorule, args, value):
    """
    Add sudo rule attr
    """
    cmd = ['ipa', 'sudorule-add-%s' % attr, testsudorule, args, value]
    multihost.master.qerun(cmd)

def sudorule_del_attr(multihost, attr, testsudorule, args, value):
    """
    Remove sudo rule attr
    """
    cmd = ['ipa', 'sudorule-remove-%s' % attr, testsudorule, args, value]
    multihost.master.qerun(cmd)


