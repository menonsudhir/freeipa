import os
from ipa_pytests.shared.rpm_utils import dnf_module_install
from ipa_pytests.shared.rpm_utils import get_rpm_version
from distutils.version import LooseVersion
from ipa_pytests.shared.yum_utils import yum_update


def is_allowed_to_update(update_to, update_from):
    ret = False
    if LooseVersion(update_to) > LooseVersion(update_from):
        ret = True
    return ret


def upgrade(host):
    """IPA upgrading"""
    rpm = get_rpm_version(host, 'ipa-server')
    print("IPA version before updating packages")
    print(rpm)
    print("starting upgrade")
    osver = host.get_os_version()
    if int(osver) < 80:
        rpms = ['ipa*', 'sssd']
        cmdupdate = yum_update(host, rpms)
        print(cmdupdate.stdout_text)
        print(cmdupdate.stderr_text)
        return cmdupdate
    else:
        dnf_module_install(host, host.config.server_module)

def modify_repo(host, repo_name, repo_url, repo_path):
    """ Method to modify the repo
    host      : host on which repo is to be set
    repo_name : repo name to be set
    repo_url  : base url for repo
    repo_path : repo path
    """
    contents = ("[{}]\n"
                "baseurl = {}\n"
                "enabled = 1\n"
                "gpgcheck = 0\n"
                "name = {}".format(repo_name.upper(),
                                   ''.join(repo_url),
                                   repo_name))
    host.put_file_contents(repo_path, contents)
