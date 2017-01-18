"""
"ipa user-* shared support utility functions
"""

from __future__ import print_function
import time
import ipa_pytests.shared.paths as paths


def add_ipa_user(host, user, passwd=None, first=None, last=None, options=None,
                 raiseonerr=True):
    """ Add an IPA user and set password """
    if passwd is None:
        passwd = "Secret123"
    if first is None:
        first = user
    if last is None:
        last = user
    chpass = 'Passw0rd1\n%s\n%s\n' % (passwd, passwd)
    print(chpass)
    host.kinit_as_admin()
    cmd = ['ipa', 'user-add',
           '--first', first,
           '--last', last,
           '--password', user]

    if options:
        for opt in options.keys():
            cmd.extend(['--' + opt, options[opt]])

    print("Running command : " + " ".join(cmd))
    op = host.run_command(cmd, stdin_text="Passw0rd1", raiseonerr=raiseonerr)
    if op.returncode == 0:
        host.run_command(['kdestroy', '-A'])
        time.sleep(2)
        cmd = host.run_command(['kinit', user], stdin_text=chpass)
        print("PASSOUT: %s" % cmd.stdout_text)
        print("PASSERR: %s" % cmd.stderr_text)
        host.kinit_as_admin()
    return op


def add_ipa_group(host, groupname, gid=None, nonposix=None, external=None, desc=None):
    """Add a ipa group """
    cmd_list = ['ipa', 'group-add', groupname]
    if gid is not None:
        cmd_list.append('--gid=' + gid)
    if nonposix is not None:
        cmd_list.append(--nonposix)
    if external is not None:
        cmd_list.append(--external)
    if desc is not None:
        cmd_list.append('--desc=' + desc)
    check = host.run_command(cmd_list, raiseonerr=False)
    return check


def del_ipa_group(host, groupname):
    """Delete ipa groups"""
    cmd_list = ['ipa', 'group-del', groupname]
    host.run_command(cmd_list)


def del_ipa_user(host, username, preserve=False, skip_err=False):
    """
    Helper function to delete IPA user
    """
    host.kinit_as_admin()
    args = []
    if preserve:
        args.append('--preserve')
    if skip_err:
        args.append('--continue')
    cmdstr = [paths.IPA, 'user-del', username] + args
    cmdstr = " ".join(cmdstr)
    cmd = host.run_command(cmdstr, raiseonerr=False)
    if cmd.returncode != 0:
        print("Failed to delete IPA user %s" % username)
    else:
        print("Successfully deleted IPA user %s" % username)
    return cmd


def show_ipa_user(host, login):
    """
    Helper function to show IPA user
    """
    host.kinit_as_admin()
    cmdstr = [paths.IPA, 'user-show', login]
    cmd = host.run_command(cmdstr, raiseonerr=False)
    return cmd


def find_ipa_user(host, login=None, options=None):
    """
    Helper function to find IPA user
    """
    host.kinit_as_admin()
    cmdstr = [paths.IPA, 'user-find']
    if options:
        for op in options.keys():
            cmdstr.extend(['--' + op, options[op]])
    if login:
        cmdstr.extend([login])
    cmd = host.run_command(cmdstr, raiseonerr=False)
    return cmd


def mod_ipa_user(host, login, options_list, raiseonerr=True):
    """
    Helper function to modify ipa user
    :param raiseonerr: boolean - set false for negative test cases
    :param host:
    :param login: string
    :param options_list: list of options to be modified
    :return:
    """
    host.kinit_as_admin()
    cmd = [paths.IPA, 'user-mod', login]
    cmd.extend(options_list)
    op = host.run_command(cmd, raiseonerr=raiseonerr)
    return op


def id_user(host, login, options_list=None, exp_returncode=0, exp_output=None):
    """
    Helper function to id
    :param host:
    :param login: string
    :param options_list: list of options
    :return:
    """
    cmd = [paths.ID, login]
    if options_list:
        cmd.extend(options_list)
    print(" ".join(cmd))
    host.qerun(cmd, exp_returncode=exp_returncode, exp_output=exp_output)


def getent(host, database, login, exp_returncode=0, exp_output=None):
    """
    Helper function to getent
    :param host:
    :param database: string
    :param login: string
    :return:
    """
    cmd = [paths.GETENT, database, login]
    host.qerun(cmd, exp_returncode=exp_returncode, exp_output=exp_output)
