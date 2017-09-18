
from ipa_pytests.shared.rpm_utils import get_rpm_version
from ipa_pytests.shared.yum_utils import add_repo, yum_update
from distutils.version import LooseVersion


def is_allowed_to_update(host):
    update_from = host.config.upgrade_from
    update_to = host.config.upgrade_to
    ret = False
    if LooseVersion(update_to) > LooseVersion(update_from):
        ret = True
    return ret


def upgrade(host, upgraderepo):
    """IPA upgrading"""
    rpm = get_rpm_version(host, 'ipa-server')
    print "IPA version before updating packages"
    print rpm
    updateto_repo = upgraderepo
    add = add_repo(host, updateto_repo)
    print "starting upgrade"
    rpms = ['ipa*', 'sssd']
    cmdupdate = yum_update(host, rpms)
    print cmdupdate.stdout_text
    print cmdupdate.stderr_text


