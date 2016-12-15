"""
This is a support library that provides functions for IPA specific
roles - add, remove, search and modify roles
"""

import ipa_pytests.shared.paths as paths


def role_add(host, role_name, options_list=None, raiseonerr=True):
    """
    Function to add a role. Options has to be specified as -['--all', '--setattr=STR',...]
    :param host:
    :param role_name: string
    :param options_list: list of all the options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = [paths.IPA, 'role-add', role_name]
    if options_list:
        cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def role_del(host, role_name, options_list=None, raiseonerr=True):
    """
    Function to delete a role
    :param host:
    :param role_name: string
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = [paths.IPA, 'role-del', role_name]
    if options_list:
        cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def role_show(host, role_name, options_list=None, raiseonerr=True):
    """
    Function to display information about a role
    :param host:
    :param role_name: string
    :param options_list: list of all the options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = [paths.IPA, 'role-show', role_name]
    if options_list:
        cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def role_find(host, role_name=None, options_list=None, raiseonerr=True):
    """
    Function to search for roles
    :param host:
    :param role_name: string
    :param options_list: list of options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = [paths.IPA, 'role-find']
    if role_name:
        cmd_list.append(role_name)
    if options_list:
        cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def role_mod(host, role_name, options_list, raiseonerr=True):
    """
    Function to modify a role
    :param host:
    :param role_name: string
    :param options_list: list of options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = [paths.IPA, 'role-mod', role_name]
    cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def role_add_privilege(host, role_name, options_list, raiseonerr=True):
    """
    Function to add privileges to a role
    :param host:
    :param role_name: string
    :param options_list: list of all options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = [paths.IPA, 'role-add-privilege', role_name]
    cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def role_remove_privilege(host, role_name, options_list, raiseonerr=True):
    """
    Function to remove privileges from a role
    :param host:
    :param role_name: string
    :param options_list: list of all options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = [paths.IPA, 'role-remove-privilege', role_name]
    cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def role_add_member(host, role_name, options_list, raiseonerr=True):
    """
    Function to add members to a role.
    :param host:
    :param role_name:
    :param options_list:
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = [paths.IPA, 'role-add-member', role_name]
    cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def role_remove_member(host, role_name, options_list, raiseonerr=True):
    """
    Function to remove members from a role
    :param host:
    :param role_name: string
    :param options_list: list of all options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = [paths.IPA, 'role-remove-member', role_name]
    cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op
