'''
Helper functions required for trust
'''

from ipa_pytests.shared.utils import (sssd_cache_reset)
import pytest
import time
import paths


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
    Helper function to id
    :param host:src/shared/trust_utils.py:126
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
