"""
hbac shared support utility functions
- hbacrule_add - add hbacrule
"""

import pytest


def sudorule_add(host, rulename, usercat=None, hostcat=None, cmdcat=None, runasusercat=None, runasgroupcat=None,
                 order=None, externaluser=None, runasexternaluser=None, runasexternalgroup=None, desc=None,
                 setattri=None, addattri=None):
    """
    Function to add a sudorule
    :param host: hostname
    :param rulename: string
    :param usercat: string
    :param hostcat: string
    :param cmdcat: string
    :param runasusercat: string
    :param runasgroupcat: string
    :param order: int
    :param externaluser: string
    :param runasexternaluser: string
    :param runasexternalgroup: string
    :param desc: string
    :param setattri: string(attr=value)
    :param addattri: string(attr=value)
    :return:
    """
    cmd_list = ['ipa', 'sudorule-add', rulename]
    if usercat is not None:
        cmd_list.append('--usercat=' + usercat)
    if hostcat is not None:
        cmd_list.append('--hostcat=' + hostcat)
    if cmdcat is not None:
        cmd_list.append('--cmdcat=' + cmdcat)
    if runasusercat is not None:
        cmd_list.append('--runasusercat=' + runasusercat)
    if runasgroupcat is not None:
        cmd_list.append('--runasgroupcat=' + runasgroupcat)
    if order is not None:
        cmd_list.append('--order=' + order.__str__())
    if externaluser is not None:
        cmd_list.append('--externaluser=' + externaluser)
    if runasexternaluser is not None:
        cmd_list.append('--runasexternaluser=' + runasexternaluser)
    if runasexternalgroup is not None:
        cmd_list.append('--runasexternalgroup=' + runasexternalgroup)
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
        print ("Error in adding sudo rule " + rulename)
    else:
        print (rulename + " has been added successfully")


def sudorule_mod(host, rulename, usercat=None, hostcat=None, cmdcat=None, runasusercat=None, runasgroupcat=None,
                 order=None, externaluser=None, runasexternaluser=None, runasexternalgroup=None, desc=None,
                 setattri=None, addattri=None):
    """
    Function to modify a sudorule
    :param host: hostname
    :param rulename: string
    :param usercat: string
    :param hostcat: string
    :param cmdcat: string
    :param runasusercat: string
    :param runasgroupcat: string
    :param order: int
    :param externaluser: string
    :param runasexternaluser: string
    :param runasexternalgroup: string
    :param desc: string
    :param setattri: string(attr=value)
    :param addattri: string(attr=value)
    :return:
    """
    cmd_list = ['ipa', 'sudorule-mod', rulename]
    if usercat is not None:
        cmd_list.append('--usercat=' + usercat)
    if hostcat is not None:
        cmd_list.append('--hostcat=' + hostcat)
    if cmdcat is not None:
        cmd_list.append('--cmdcat=' + cmdcat)
    if runasusercat is not None:
        cmd_list.append('--runasusercat=' + runasusercat)
    if runasgroupcat is not None:
        cmd_list.append('--runasgroupcat=' + runasgroupcat)
    if order is not None:
        cmd_list.append('--order=' + order.__str__())
    if externaluser is not None:
        cmd_list.append('--externaluser=' + externaluser)
    if runasexternaluser is not None:
        cmd_list.append('--runasexternaluser=' + runasexternaluser)
    if runasexternalgroup is not None:
        cmd_list.append('--runasexternalgroup=' + runasexternalgroup)
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
        print ("Error in modifying sudo rule " + rulename)
    else:
        print (rulename + " has been modified successfully")


def sudorule_add_option(host, rulename, sudooption):
    """
    Function to add options to sudorule
    :param host: hostname:string
    :param rulename: string
    :param sudooption: string
    :return:
    """
    cmd_list = ['ipa', 'sudorule-add-option', rulename, '--sudooption', sudooption]
    host.run_command(cmd_list)


def sudorule_find(host, rulename=None):
    """
    Function to find all the sudorules
    :param host: hostname : string
    :return:
    """
    cmd_list = ['ipa', 'sudorule-find']
    if rulename is not None:
        cmd_list.append(rulename)
    op = host.run_command(cmd_list)
    return op


def sudorule_del(host, rulename):
    """
    Function to delete a sudorule
    :param host: hostname: string
    :param rulename: string
    :return:
    """
    cmd_list = ['ipa', 'sudorule-del', rulename]
    host.run_command(cmd_list)
