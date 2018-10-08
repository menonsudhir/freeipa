'''
Helper functions required for trust
'''

import pytest
import time
from datetime import datetime, timedelta
from ipa_pytests.shared import paths


def ipa_trust_show(host, domain, options_list=None, raiseonerr=True):
    """
    Helper function to id
    :param host:
    :param domain: string
    :param options_list: list of options
    :return:
    """
    cmd_list = [paths.IPA, 'trust-show', domain]
    if options_list:
        cmd_list.extend(options_list)
    op = host.run_command(cmd_list, raiseonerr=raiseonerr)
    return op


def ipa_trust_add(host, addomain, login, options_list=None, stdin_text=None, raiseonerr=True):
    """
    Helper function to trust add
    :param host: string
    :param addomain: string
    :param login: string
    :param options_list: list of options
    :return:
    """
    host.kinit_as_admin()
    cmd_list = [paths.IPA, 'trust-add', addomain, '--admin', login]
    if options_list:
        cmd_list.extend(options_list)
    op = host.run_command(cmd_list, stdin_text=stdin_text, raiseonerr=raiseonerr)
    return op

def check_for_skew(master, addomain):
    """
    Helper function for checking skew
    :param master : string
    :param addomain : string
    :return:
    """
    # Check time between two server
    cmdstr = "date +'%Y,%m,%d,%H,%M,%S'"
    serdate = master.run_command(cmdstr).stdout_text.strip()
    adsdate = addomain.run_command(cmdstr).stdout_text.strip()
    # Convert str date into date object
    sdate = datetime.strptime(serdate, '%Y,%m,%d,%H,%M,%S')
    cdate = datetime.strptime(adsdate, '%Y,%m,%d,%H,%M,%S')
    oneminute = timedelta(minutes=1)
    # If clock skew between IPA master and AD Server is greater than
    # one minute then fail
    skew = sdate - cdate
    if skew > oneminute:
        return False
    else:
        return True
