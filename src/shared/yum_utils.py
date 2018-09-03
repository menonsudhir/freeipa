"""
yum - shared support utility functions
- check_rpm - Helper function to check if packages are installed
- list_rpms - Helper function to list installed rpms
- remove_rpm - Helper function to remove installed rpms
"""

from ipa_pytests.shared import paths
from ipa_pytests.shared.rpm_utils import check_rpm


def add_repo(host, repo_url):
    """ add repo file"""

    path = '/etc/yum.repos.d/upgrade.repo'
    contents = '[upgrade-repo]\nname=upgrade repo\ngpgcheck=0\nenabled=1\n'
    contents += 'baseurl=%s' % repo_url
    host.put_file_contents(path, contents)
    yumplugin = '/etc/yum/pluginconf.d/priorities.conf'
    if host.transport.file_exists(yumplugin):
        host.run_command(['mv', yumplugin,
                          '%s.qebackup' % yumplugin])
        conf_contents = '[main]\nenabled = 0'
        host.put_file_contents(yumplugin, conf_contents)


def yum_update(host, rpm_list):
    """Updating packages"""
    run_cmd = [paths.YUM, 'update', '-y', '--nogpgcheck']
    run_cmd += rpm_list
    cmd1 = host.run_command(run_cmd, raiseonerr=False)
    return cmd1


def yum_install(host, rpm_list1):

    list2 = rpm_list1
    cmd2 = host.run_command([paths.YUM, 'install', '-y', list2], raiseonerr=True)
