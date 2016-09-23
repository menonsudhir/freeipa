"""
"ipa user-* shared support utility functions
"""

import time
import paths


def add_ipa_user(host, user, passwd=None, first=None, last=None, options=None):
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

    print("Runngin command : " + " ".join(cmd))
    host.run_command(cmd, stdin_text="Passw0rd1")
    host.run_command(['kdestroy', '-A'])
    time.sleep(2)
    cmd = host.run_command(['kinit', user], stdin_text=chpass)
    print("PASSOUT: %s" % cmd.stdout_text)
    print("PASSERR: %s" % cmd.stderr_text)
    host.kinit_as_admin()


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


def user_show(host, username):
    """
    Helper function to show IPA user
    """
    host.kinit_as_admin()
    cmdstr = [paths.IPA, 'user-show', username]
    cmd = host.run_command(cmdstr, raiseonerr=False)
    return cmd


def user_find(host, username=None, options=None):
    """
    Helper function to find IPA user
    """
    host.kinit_as_admin()
    cmdstr = [paths.IPA, 'user-find']
    if options:
        for op in options.keys():
            cmdstr.extend(['--' + op, options[op]])
    if username:
        cmdstr.extend([username])
    cmd = host.run_command(cmdstr, raiseonerr=False)
    return cmd
