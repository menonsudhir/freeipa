'''
Helper functions required for ssh from client machine
'''

from ipa_pytests.shared.utils import (sssd_cache_reset)
import pytest
import time
from ipa_pytests.shared import paths


def ssh_from_client(multihost):
    """
    ssh to user from client environment
    """
    ad1 = multihost.ads[0]
    addomain = '.'.join(ad1.hostname.split(".")[1:])
    aduser = '{}@{}'.format(multihost.aduser, addomain)

    # cleaning sssd cache
    # sssd_cache_reset(multihost.master)
    # print("waiting for 60 seconds")
    # time.sleep(60)

    # temp fix for bz1659498
    sssd_cache_reset(multihost.master, wait_sssd_operational=True, user=aduser)

    expect_script = 'set timeout 15\n'
    expect_script = 'spawn ssh -l ' + multihost.aduser + '@' + \
                    addomain + ' ' + multihost.master.ip + '\n'
    expect_script += 'expect "Password:"\n'
    expect_script += 'send "' + multihost.password + '\r"\n'
    expect_script += 'expect "$"\n'
    expect_script += 'send "id\r"\n'
    expect_script += 'expect "uid=*"\n'
    expect_script += 'expect EOF\n'
    output = multihost.client.expect(expect_script)
    print("ssh successfully from client")
