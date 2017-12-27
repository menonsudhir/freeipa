"""
yum - shared support utility functions
- check_rpm - Helper function to check if packages are installed
- list_rpms - Helper function to list installed rpms
- remove_rpm - Helper function to remove installed rpms
"""

import paths
from rpm_utils import check_rpm


def add_repo(host, repo_url):
    """ add repo file"""

    cmd = check_rpm(host, ['yum-utils'])
    nogpgcheck = [paths.YUMCONFIGMANAGER, '--setopt=\*.gpgcheck=0', '--save']
    cmd2 = host.run_command(nogpgcheck, raiseonerr=False)
    yum_add = [paths.YUMCONFIGMANAGER, '--add-repo=%s' % repo_url]
    cmd = host.run_command(yum_add, raiseonerr=False)


def yum_update(host, rpm_list):
    """Updating packages"""
    run_cmd = [paths.YUM, 'update', '-y', '--nogpgcheck']
    run_cmd += rpm_list
    cmd1 = host.run_command(run_cmd, raiseonerr=False)
    return cmd1


def yum_install(host, rpm_list1):

    list2 = rpm_list1
    cmd2 = host.run_command([paths.YUM, 'install', '-y', list2], raiseonerr=True)
