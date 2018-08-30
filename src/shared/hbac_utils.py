"""
hbac shared support utility functions
- hbacrule_add - add hbacrule
"""

import pytest


def hbacrule_add(host, rulename, usercat=None, hostcat=None, servicecat=None, desc=None, setattri=None, addattri=None):
    """
    Function to add a hbac rule
    :param host: multihost.host
    :param rulename: rule_name - string
    :param usercat: string
    :param hostcat: string
    :param servicecat: string
    :param desc: string
    :param setattr: string
    :param addattr: string
    :return: None
    """
    cmd_list = ['ipa', 'hbacrule-add', rulename]
    if usercat is not None:
        cmd_list.append('--usercat=' + usercat)
    if hostcat is not None:
        cmd_list.append('--hostcat=' + hostcat)
    if servicecat is not None:
        cmd_list.append('--servicecat=' + servicecat)
    if desc is not None:
        cmd_list.append('--desc=' + desc)
    if setattri is not None:
        cmd_list.append('--setattr' + setattri)
    if addattri is not None:
        cmd_list.append('--addattr' + addattri)
    check = host.run_command(cmd_list,
                             set_env=True,
                             raiseonerr=False)
    if check.returncode != 0:
        print("Error in adding hbac rule" + rulename)
    else:
        print(rulename + "has been added successfully")


def hbacrule_del(host, rulename):
    """
    Function th delete a particular hbac rule
    :param host:
    :param rulename:
    :return:
    """
    cmd_list = ['ipa', 'hbacrule-del', rulename]
    host.run_command(cmd_list)


def hbacrule_find(host, rulename=None, exp_output=None):
    """
    Function to check all the hbac rules available (incase of rulename=None)
    :param host: honstname : string
    :param rulename: string
    :return:
    """
    cmd_list = ['ipa', 'hbacrule-find']
    if rulename is not None:
        cmd_list.append(rulename)

    if exp_output is None:
        op = host.run_command(cmd_list,
                              set_env=True,
                              raiseonerr=False)
        return op
    else:
        host.qerun(cmd_list,
                   exp_output=exp_output)
