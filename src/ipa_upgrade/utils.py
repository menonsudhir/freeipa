import os
from ipa_pytests.shared.rpm_utils import get_rpm_version
from ipa_pytests.shared.yum_utils import add_repo, yum_update
from distutils.version import LooseVersion
from selenium import webdriver


def is_allowed_to_update(update_to, update_from):
    ret = False
    if LooseVersion(update_to) > LooseVersion(update_from):
        ret = True
    return ret


def upgrade(host):
    """IPA upgrading"""
    rpm = get_rpm_version(host, 'ipa-server')
    print "IPA version before updating packages"
    print rpm
    print "starting upgrade"
    rpms = ['ipa*', 'sssd']
    cmdupdate = yum_update(host, rpms)
    print cmdupdate.stdout_text
    print cmdupdate.stderr_text
    return cmdupdate


