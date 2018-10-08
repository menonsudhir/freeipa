'''
Helper functions required for test_external-trust
'''
from ipa_pytests.shared.utils import (sssd_cache_reset)
import pytest
import time
from ipa_pytests.shared.trust_utils import (ipa_trust_add)


def ad_domain(multihost):
    """
    AD Domain
    """
    ad1 = multihost.ads[0]
    addomain = '.'.join(ad1.external_hostname.split(".")[1:])

    return addomain


def add_external_trust(multihost):
    """
    Add external trust
    """
    ad1 = multihost.ads[0]
    forwardzone = '.'.join(ad1.external_hostname.split(".")[1:])

    # trust-add
    opt_list = ['--type=ad', '--external=true']
    passwd = ad1.ssh_password
    cmd = ipa_trust_add(multihost.master, forwardzone, ad1.ssh_username, opt_list, passwd)
    print("ipa trust-add \n: {}".format(cmd.stdout_text))

    if "Trust type: Non-transitive external trust to a " \
       "domain in another Active Directory forest" in cmd.stdout_text:
        print("Expected Result:\n External trust added successfully\n")
    else:
        pytest.xfail("External trust not added")
