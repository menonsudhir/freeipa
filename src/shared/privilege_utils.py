"""
This is a support library that provides functions for IPA specific
privileges - add, remove, search and modify privileges
"""

import ipa_pytests.shared.paths as paths


def privilege_add(host, privilege_name, options_list=None, raiseonerr=True):
    """
    Function to add a privilege. Options has to be specified as -['--all', '--setattr=STR',...]
    :param host:
    :param privilege_name: string
    :param options_list: list of all the options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = [paths.IPA, 'privilege-add', privilege_name]
    if options_list:
        cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def privilege_del(host, privilege_name, raiseonerr=True):
    """
    Function to delete a privilege
    :param host:
    :param privilege_name: string
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = [paths.IPA, 'privilege-del', privilege_name]
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def privilege_show(host, privilege_name, options_list=None, raiseonerr=True):
    """
    Function to display information about a privilege
    :param host:
    :param privilege_name: string
    :param options_list: list of all the options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = [paths.IPA, 'privilege-show', privilege_name]
    if options_list:
        cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def privilege_find(host, privilege_name=None, options_list=None, raiseonerr=True):
    """
    Function to search for privileges
    :param host:
    :param privilege_name: string
    :param options_list: list of options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = [paths.IPA, 'privilege-find']
    if privilege_name:
        cmd_list.append(privilege_name)
    if options_list:
        cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def privilege_mod(host, privilege_name, options_list, raiseonerr=True):
    """
    Function to modify a privilege
    :param host:
    :param privilege_name: string
    :param options_list: list of options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = [paths.IPA, 'privilege-mod', privilege_name]
    cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def privilege_add_permission(host, privilege_name, options_list, raiseonerr=True):
    """
    Function to add permissions to a privilege
    :param host:
    :param privilege_name: string
    :param options_list: list of all options(permission is must)
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = [paths.IPA, 'privilege-add-permission', privilege_name]
    cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def privilege_remove_permission(host, privilege_name, options_list, raiseonerr=True):
    """
    Function to remove permissions from a privilege
    :param host:
    :param privilege_name: string
    :param options_list: list of all options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = [paths.IPA, 'privilege-remove-permission', privilege_name]
    cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op
