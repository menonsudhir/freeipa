"""
"ipa user-* shared support utility functions
- add_ipa_user - add user and set password
- del_ipa_user - Delete IPA user
"""

import time
import paths


def add_ipa_user(host, user, passwd=None, first=None, last=None):
    """ Add an IPA user and set password """
    if passwd is None:
        passwd = "Secret123"
    if first is None:
        first = user
    if last is None:
        last = user
    chpass = 'Passw0rd1\n%s\n%s\n' % (passwd, passwd)
    print (chpass)
    host.kinit_as_admin()
    host.run_command(['ipa', 'user-add', "--first", first, "--last", last,
                      "--password", user], stdin_text="Passw0rd1")
    host.run_command(['kdestroy', '-A'])
    time.sleep(2)
    cmd = host.run_command(['kinit', user], stdin_text=chpass)
    print ("PASSOUT: %s" % cmd.stdout_text)
    print ("PASSERR: %s" % cmd.stderr_text)
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
