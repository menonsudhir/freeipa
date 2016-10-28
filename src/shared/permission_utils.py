"""
This is a support library that provides functions for IPA specific
permissions - add, remove, search and modify permissions
"""


def permission_add(host, permission_name, options_list, raiseonerr=True):
    """
    Function to add a permission. Options has to be specified as ['--right=all', '--type=STR',...]
    :param host:
    :param permission_name: string
    :param options_list: list of all the options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = ['ipa', 'permission-add', permission_name]
    cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def permission_del(host, permission_name, options_list=None, raiseonerr=True):
    """
    Function to delete a permission
    :param host:
    :param permission_name: string
    :param options_list: list of all the options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = ['ipa', 'permission-del']
    if permission_name:
        cmd_list.append(permission_name)
    if options_list:
        cmd_list.extend(options_list)
    print (" ".join(cmd_list))
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def permission_show(host, permission_name, options_list=None, raiseonerr=True):
    """
    Function to display information about a permission
    :param host:
    :param permission_name: string
    :param options_list: list of all the options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = ['ipa', 'permission-show', permission_name]
    if options_list:
        cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def permission_find(host, permission_name=None, options_list=None, raiseonerr=True):
    """
    Function to search for permissions
    :param host:
    :param permission_name: string
    :param options_list: list of options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = ['ipa', 'permission-find']
    if permission_name:
        cmd_list.append(permission_name)
    if options_list:
        cmd_list.extend(options_list)
    print (" ".join(cmd_list))
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def permission_mod(host, permission_name, options_list, raiseonerr=True):
    """
    Function to modify a permission
    :param host:
    :param permission_name: string
    :param options_list: list of options
    :param raiseonerr: boolean - False for negative testcases
    :return:
    """
    cmd_list = ['ipa', 'permission-mod', permission_name]
    cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op
